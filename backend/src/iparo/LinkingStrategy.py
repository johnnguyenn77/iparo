import random
from abc import abstractmethod, ABC
from datetime import timedelta
from math import floor

from iparo.Exceptions import IPARONotFoundException
from iparo.IPARODateConverter import IPARODateConverter
from iparo.IPAROLink import IPAROLink
from iparo.IPAROLinkFactory import IPAROLinkFactory
from iparo.IPFS import ipfs
from iparo.IPNS import ipns


# Make package/renaming with __init__ file

class LinkingStrategy(ABC):
    """
    The linking strategy determines how the new IPARO is to be linked. The IPARO
    object is first linked using the linking strategy, created (with the links),
    and then finally stored.
    """

    @abstractmethod
    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        pass


class SingleStrategy(LinkingStrategy):

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        return {IPAROLinkFactory.from_cid(latest_cid)}


class ComprehensiveStrategy(LinkingStrategy):

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        latest_iparo = ipfs.retrieve(latest_cid)
        linked_iparos = latest_iparo.linked_iparos
        latest_iparo_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_iparo)
        if latest_iparo_link is not None:
            linked_iparos.add(latest_iparo_link)

        return linked_iparos


class KPreviousStrategy(LinkingStrategy):

    def __init__(self, k: int):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        cid = ipns.get_latest_cid(url)
        latest_iparo = ipfs.retrieve(cid)
        linked_iparos = latest_iparo.linked_iparos
        latest_link = IPAROLinkFactory.from_cid_iparo(cid, latest_iparo)
        linked_iparos.add(latest_link)

        seq_num_to_drop = max(latest_iparo.seq_num - self.k, 0)
        if seq_num_to_drop > 0:
            iparo_link_to_drop = IPAROLinkFactory.retrieve_nth_iparo(latest_link, seq_num_to_drop)
            linked_iparos.remove(iparo_link_to_drop)

        return linked_iparos


class PreviousStrategy(KPreviousStrategy):

    def __init__(self):
        super().__init__(1)


class KRandomStrategy(LinkingStrategy):

    def __init__(self, k: int):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        links = set()
        latest_cid = ipns.get_latest_cid(url)
        latest_node = ipfs.retrieve(latest_cid)
        latest_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_node)
        links.add(latest_link)

        latest_node_links = latest_node.linked_iparos
        first_link = IPAROLinkFactory.retrieve_nth_iparo(latest_link, 0)
        links.add(first_link)

        num_nodes = latest_node.seq_num
        if num_nodes <= self.k:
            links.update(latest_node_links)
        else:
            # K random sequence numbers from 1 to n-1, n = latest sequence number
            candidate_seq_nums = random.sample(range(1, num_nodes), min(self.k, num_nodes-1))
            IPAROLinkFactory.from_indices(latest_link, candidate_seq_nums)
            links.update({IPAROLinkFactory.from_cid(ipfs.retrieve_by_number(url, seq_num))
                          for seq_num in candidate_seq_nums})
        return links


class SequentialExponentialStrategy(LinkingStrategy):

    def __init__(self, k: float):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        latest_link = IPAROLinkFactory.from_cid(latest_cid)
        node_num = latest_link.seq_num
        indices: set[int] = {0, node_num}
        index = 1.0
        while index < node_num + 1:
            indices.add(node_num - floor(index - 1))
            index *= self.k
        links = IPAROLinkFactory.from_indices(latest_link, indices)
        return links


class SequentialUniformNPriorStrategy(LinkingStrategy):

    def __init__(self, n: int):
        self.n = n

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        latest_link = IPAROLinkFactory.from_cid(latest_cid)
        node_num = latest_link.seq_num

        indices: set[int] = {node_num * i // (self.n + 1) for i in range(self.n + 2)}
        return IPAROLinkFactory.from_indices(latest_link, indices)


class SequentialSMaxGapStrategy(LinkingStrategy):

    # s: the number of hops allowed between linked nodes.
    def __init__(self, s: int):
        self.s = s

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:

        latest_cid = ipns.get_latest_cid(url)
        if latest_cid is None:
            return set()

        latest_node = ipfs.retrieve(latest_cid)
        latest_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_node)
        links = {latest_link}

        if latest_node.seq_num == 0:
            return links

        # Add first version if exists
        first_cid = ipfs.retrieve_by_number(url, 0)
        first_link = IPAROLinkFactory.from_cid(first_cid)
        links.add(first_link)

        # Add the immediate previous version
        previous_cid = ipfs.retrieve_by_number(url, latest_node.seq_num - 1)
        previous_link = IPAROLinkFactory.from_cid(previous_cid)
        links.add(previous_link)


        # Sequentially add nodes with no more than S hops between them
        current_seq_num = latest_node.seq_num - 1

        # S: size -> N (N*S = total size)
        while current_seq_num > 0:
            current_seq_num = max(current_seq_num - self.s, 0)
            current_cid = ipfs.retrieve_by_number(url, current_seq_num)
            current_link = IPAROLinkFactory.from_cid(current_cid)
            links.add(current_link)

        return links


class TemporallyUniformStrategy(LinkingStrategy):
    def __init__(self, n: int):
        self.n = n  # Number of uniformly distributed links to create

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        latest_link = IPAROLinkFactory.from_cid(latest_cid)
        first_link = IPAROLinkFactory.retrieve_nth_iparo(latest_link, 0)

        latest_timestamp = IPARODateConverter.str_to_datetime(latest_link.timestamp)
        first_timestamp = IPARODateConverter.str_to_datetime(first_link.timestamp)

        links = {first_link, latest_link}

        time_window = latest_timestamp - first_timestamp

        # Adds nodes sequenced as 1, 2, ..., n-1
        timestamps = {first_timestamp + i * time_window / self.n for i in range(1, self.n)}
        try:
            links.update(IPAROLinkFactory.from_timestamps(latest_link, timestamps))
        except IPARONotFoundException:
            pass

        return links


class TemporallyMaxGapStrategy(LinkingStrategy):
    def __init__(self, max_gap: timedelta):
        self.max_gap = max_gap

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        latest_node = ipfs.retrieve(latest_cid)
        latest_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_node)

        # Add first version if exists
        first_link = IPAROLinkFactory.retrieve_nth_iparo(latest_link, 0)
        links = {first_link, latest_link}

        # Keep stepping back using max_gap
        current_time = IPARODateConverter.str_to_datetime(latest_node.timestamp)
        curr_link = latest_link
        try:
            while True:
                target_time = current_time - self.max_gap
                curr_link = IPAROLinkFactory.retrieve_closest_iparo(curr_link, target_time)
                # Get closest, then conditionally
                if target_time < IPARODateConverter.str_to_datetime(curr_link.timestamp):
                    curr_link = IPAROLinkFactory.retrieve_nth_iparo(curr_link, curr_link.seq_num - 1)
                    current_time = IPARODateConverter.str_to_datetime(curr_link.timestamp)
                links.add(curr_link)
        finally:
            return links


class TemporallyExponentialStrategy(LinkingStrategy):
    def __init__(self, base: float, time_unit: timedelta):
        self.base = base
        self.time_unit = time_unit

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        latest_link = IPAROLinkFactory.from_cid(latest_cid)

        # Add first version if exists
        first_link = IPAROLinkFactory.retrieve_nth_iparo(latest_link, 0)

        # Exponential time gaps
        current_time = IPARODateConverter.str_to_datetime(latest_link.timestamp)
        gap = self.time_unit
        first_time = IPARODateConverter.str_to_datetime(first_link.timestamp)
        timestamps = {current_time, first_time}
        while current_time - gap > first_time:
            timestamps.add(current_time - gap)
            gap *= self.base
        try:
            links = IPAROLinkFactory.from_timestamps(latest_link, timestamps)
        except IPARONotFoundException:
            links = set()

        links.add(first_link)
        links.add(latest_link)

        return links
