import random
from abc import abstractmethod, ABC
from math import floor

from iparo.IPAROLink import IPAROLink
from iparo.IPAROLinkFactory import IPAROLinkFactory
from iparo.IPFS import ipfs, Mode
from iparo.IPNS import ipns
from iparo.TimeUnit import TimeUnit


# Make package/renaming with __init__ file

class LinkingStrategy(ABC):
    """
    The linking strategy determines how the new IPARO is to be linked. The IPARO
    object is first linked using the linking strategy, created (with the links),
    and then finally stored. It depends on the implementation of the IPNS and the IPFS.
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
        latest_node_links, latest_link, _ = IPAROLinkFactory.get_latest_node_links(url)
        latest_node_links.add(latest_link)

        return latest_node_links


class KPreviousStrategy(LinkingStrategy):
    def __init__(self, k: int):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        linked_iparos, latest_link, latest_iparo = IPAROLinkFactory.get_latest_node_links(url)

        seq_num_to_drop = max(latest_link.seq_num - self.k, 0)
        if seq_num_to_drop > 0:
            iparo_link_to_drop = ipfs.retrieve_nth_iparo(seq_num_to_drop, latest_link)
            linked_iparos.remove(iparo_link_to_drop)

        return linked_iparos


class PreviousStrategy(KPreviousStrategy):

    def __init__(self):
        super().__init__(1)


class KRandomStrategy(LinkingStrategy):

    def __init__(self, k: int):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_node_links, latest_link, latest_iparo = IPAROLinkFactory.get_latest_node_links(url)

        num_nodes = latest_link.seq_num
        if num_nodes <= self.k:
            latest_node_links.add(latest_link)
            return latest_node_links
        else:
            # K random sequence numbers from 1 to n-1, n = latest sequence number
            candidate_seq_nums = set(random.sample(range(1, num_nodes), min(self.k, num_nodes - 1)))
            candidate_seq_nums.add(0)
            links = IPAROLinkFactory.from_indices(latest_link, set(candidate_seq_nums))
        links.add(latest_link)
        return links


class SequentialExponentialStrategy(LinkingStrategy):

    def __init__(self, k: float):
        self.k = k

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        latest_link = ipfs.get_latest_link(url)
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
        latest_link, latest_iparo = IPAROLinkFactory.get_link_to_latest_node(url)
        indices: set[int] = {latest_iparo.seq_num * i // (self.n + 1) for i in range(self.n + 2)}
        return IPAROLinkFactory.from_indices(latest_link, indices)


class SequentialSMaxGapStrategy(LinkingStrategy):

    # s: the number of hops allowed between linked nodes.
    def __init__(self, s: int):
        self.s = s

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        first_link, latest_link, latest_iparo = IPAROLinkFactory.get_links_to_first_and_latest_nodes(url)

        # Sequentially add nodes with no more than S hops between them
        start_seq_num = latest_link.seq_num - self.s

        # range(start, 0, -s) -> From start to 0 (exclusive), going down in step of size s.
        node_indices = set(range(start_seq_num, 0, -self.s))
        links = IPAROLinkFactory.from_indices(latest_link, node_indices)
        links.add(first_link)
        links.add(latest_link)

        return links


class TemporallyUniformStrategy(LinkingStrategy):
    def __init__(self, n: int):
        self.n = n  # Number of uniformly distributed links to create

    # Do latest iparo extraction outside.
    # Supply known links?
    def get_candidate_nodes(self, latest_iparo: IPARO, latest_link: IPAROLink) -> set[IPAROLink]:
        first_link, latest_link, latest_iparo = IPAROLinkFactory.get_links_to_first_and_latest_nodes(url)
        time_window = latest_link.timestamp - first_link.timestamp
        first_ts = first_link.timestamp
        # Adds nodes sequenced as 1, 2, ..., n-1
        timestamps = {int(first_ts + i * time_window / self.n) for i in range(1, self.n)}

        # from_timestamps(timestamps: set[int], known_links: set[IPAROLink])
        links, _ = IPAROLinkFactory.from_timestamps(latest_link, {first_link, latest_link}, timestamps)

        # Add latest and first links.
        links.add(first_link)
        links.add(latest_link)

        return links


class TemporallyMinGapStrategy(LinkingStrategy):
    def __init__(self, max_gap: float):
        """
        The maximum gap is in terms of seconds.
        """
        self.max_gap = max_gap

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        first_link, latest_link, latest_iparo = IPAROLinkFactory.get_links_to_first_and_latest_nodes(url)
        curr_link = latest_link
        current_time = latest_link.timestamp
        known_links = {first_link, latest_link}

        links = set()
        # Keep stepping back using max_gap (Earliest?)
        # Example: * * - * - - - - * * - - * *
        # * = capture, - = no capture
        while curr_link.seq_num > 0:
            current_time = current_time - self.max_gap * TimeUnit.SECONDS
            # Choose earliest after but with the caveat that if there is no link within that window,
            # we extend the window.
            curr_link, known_links = ipfs.retrieve_closest_iparo(curr_link, known_links,
                                                                 current_time, Mode.EARLIEST_AFTER)
            links.add(curr_link)

        links.add(first_link)
        links.add(latest_link)
        return links


class TemporallyExponentialStrategy(LinkingStrategy):
    def __init__(self, base: float, time_unit: int):
        self.base = base
        self.time_unit = time_unit

    def get_candidate_nodes(self, url: str) -> set[IPAROLink]:
        # Assume num_nodes > 1
        first_link, latest_link, latest_iparo = IPAROLinkFactory.get_links_to_first_and_latest_nodes(url)

        # Exponential time gaps
        gap = self.time_unit
        time_window = latest_iparo.timestamp - first_link.timestamp
        gaps = []
        while gap < time_window:
            gaps.append(-gap)
            gap *= self.base
        gaps.reverse()

        timestamps = {latest_iparo.timestamp + gap for gap in gaps}
        links, _ = IPAROLinkFactory.from_timestamps(latest_link, {first_link, latest_link}, timestamps)
        links.add(first_link)
        links.add(latest_link)

        return links
