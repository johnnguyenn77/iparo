import random
from abc import abstractmethod, ABC
from datetime import timedelta
from math import floor

from iparo.IPARODateConverter import IPARODateConverter
from iparo.IPAROLink import IPAROLink
from iparo.IPAROLinkFactory import IPAROLinkFactory
from iparo.IPFS import ipfs, Mode
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
        if latest_cid is None:
            return set()
        return {IPAROLinkFactory.from_cid(latest_cid)}


class ComprehensiveStrategy(LinkingStrategy):

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        if latest_cid is None:
            # First link
            return set()

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
        if cid is None:
            # First link
            return set()
        latest_iparo = ipfs.retrieve(cid)
        linked_iparos = latest_iparo.linked_iparos
        # Drop 1 node and add the latest node when... length is k+1?
        # max(0, Length of linked iparos - k), only if positive.
        linked_iparos.add(IPAROLinkFactory.from_cid_iparo(cid, latest_iparo))

        if len(linked_iparos) == self.k + 2:

            seq_num_to_drop = max(latest_iparo.seq_num - self.k, 0)
            if seq_num_to_drop > 0:
                # Ensure not none.
                node_to_drop = [node for node in linked_iparos if node.seq_num == seq_num_to_drop][0]
                linked_iparos.remove(node_to_drop)

        # iparo_links = [link for link in iparo.linked_iparos if link.seq_num == iparo.seq_num - 1]
        # while len(iparo_links) > 0 and len(linked_iparos) < self.k + 1:
        #     # TODO: Optimize
        #     link = iparo_links[0]
        #     linked_iparos.add(link)
        #     cid = link.cid
        #     iparo = ipfs.retrieve(cid)
        #     iparo_links = [link for link in iparo.linked_iparos if link.seq_num == iparo.seq_num - 1]

        return linked_iparos


class PreviousStrategy(KPreviousStrategy):

    def __init__(self):
        super().__init__(1)


class KRandomStrategy(LinkingStrategy):

    def __init__(self, k_min: int, k_max: int):
        self.k_min = k_min
        self.k_max = k_max

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        k = random.randint(self.k_min, self.k_max)
        # Check if the number of linked CIDs is greater than K and add K-1 random linked CIDs
        latest_cid = ipns.get_latest_cid(url)
        if latest_cid is None:
            return set()

        latest_node = ipfs.retrieve(latest_cid)
        latest_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_node)

        if latest_node.seq_num == 0:
            return {latest_link}
        if latest_node.seq_num >= k-1:
            pass

        # First link is present from latest note links
        latest_node_links = latest_node.linked_iparos
        first_link = [link for link in latest_node_links if link.seq_num == 0][0]

        links = {first_link, latest_link}
        num_nodes = latest_node.seq_num
        if num_nodes <= k:
            links = links.union(latest_node_links)
            return links

        # K random sequence numbers from 1 to n-1, n = latest sequence number
        candidate_seq_nums = random.sample(range(1, num_nodes), min(k, num_nodes-1))  # To sort in reverse?

        links = links.union({IPAROLinkFactory.from_cid(
            ipfs.retrieve_by_number(url, seq_num)) for seq_num in candidate_seq_nums})

        return links


class SequentialExponentialStrategy(LinkingStrategy):

    def __init__(self, k: float):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_cid = ipns.get_latest_cid(url)
        if latest_cid is None:
            return set()
        latest_node = ipfs.retrieve(latest_cid)
        node_num = latest_node.seq_num
        if node_num == 0:
            return {IPAROLinkFactory.from_cid_iparo(latest_cid, latest_node)}
        # Required: node_num >= 2
        indices: set[int] = {0, node_num}
        index = 1.0
        while index < node_num + 1:
            indices.add(node_num + 1 - floor(index))
            index *= self.k

        links = set()

        for i in indices:
            cid = ipfs.retrieve_by_number(url, i)
            link = IPAROLinkFactory.from_cid(cid)
            if link is not None:
                links.add(link)

        return links


class SequentialUniformNPriorStrategy(LinkingStrategy):

    def __init__(self, n: int):
        self.n = n

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        # Special case: No nodes in collection
        latest_cid = ipns.get_latest_cid(url)
        if latest_cid is None:
            return set()
        latest_node = ipfs.retrieve(latest_cid)
        node_num = latest_node.seq_num
        indices: set[int] = {node_num * i // (self.n + 1) for i in range(self.n + 2)}

        links = set()

        for i in indices:
            cid = ipfs.retrieve_by_number(url, i)
            link = IPAROLinkFactory.from_cid(cid)
            if link is not None:
                links.add(link)

        return links


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
        while current_seq_num > 0:
            next_seq_num = max(current_seq_num - self.s, 0)
            if next_seq_num == current_seq_num:
                break

            next_cid = ipfs.retrieve_by_number(url, next_seq_num)
            next_link = IPAROLinkFactory.from_cid(next_cid)
            links.add(next_link)

            current_seq_num = next_seq_num

        return links


class TemporallyUniformStrategy(LinkingStrategy):
    def __init__(self, n: int):
        self.n = n  # Number of uniformly distributed links to create

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

        # Uniformly distribute N prior versions
        # TODO: Optimize
        latest_timestamp = IPARODateConverter.str_to_datetime(latest_node.timestamp)
        first_timestamp = IPARODateConverter.str_to_datetime(first_link.timestamp)
        time_window = latest_timestamp - first_timestamp
        for i in range(1, self.n + 1):
            target_time = latest_timestamp - (time_window * i / (self.n + 1))
            cid = ipfs.retrieve_by_timestamp(url, target_time, Mode.CLOSEST)
            if cid:
                links.add(IPAROLinkFactory.from_cid(cid))

        return links


class TemporallyMaxGapStrategy(LinkingStrategy):
    def __init__(self, max_gap: timedelta):
        self.max_gap = max_gap

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

        # Keep stepping back using max_gap
        current_time = IPARODateConverter.str_to_datetime(latest_node.timestamp)
        while True:
            target_time = current_time - self.max_gap
            cid = ipfs.retrieve_by_timestamp(url, target_time, Mode.LATEST_BEFORE)
            if not cid or cid in [link.cid for link in links]:
                break
            node = ipfs.retrieve(cid)
            if not node:
                break
            links.add(IPAROLinkFactory.from_cid(cid))
            current_time = IPARODateConverter.str_to_datetime(latest_node.timestamp)

        return links


class TemporallyExponentialStrategy(LinkingStrategy):
    def __init__(self, base: float, time_unit: timedelta):
        self.base = base
        self.time_unit = time_unit

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

        # Exponential time gaps
        current_time = IPARODateConverter.str_to_datetime(latest_node.timestamp)

        power = 0

        # Our stop condition is when the gap exceeds the time gap between the first and latest nodes,
        # by at least a factor of the base.
        while True:
            gap = self.time_unit * (self.base ** power)
            target_time = current_time - gap

            cid = ipfs.retrieve_by_timestamp(url, target_time, Mode.CLOSEST)
            if not cid or cid == first_cid:
                break
            link = IPAROLinkFactory.from_cid(cid)
            if link:
                links.add(link)

            power += 1

        return links
