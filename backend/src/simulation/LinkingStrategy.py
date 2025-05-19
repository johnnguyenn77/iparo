import random
from abc import abstractmethod, ABC
from math import floor

from simulation.IPARO import IPARO
from simulation.IPAROLink import IPAROLink
from simulation.IPAROLinkFactory import IPAROLinkFactory
from simulation.IPFS import ipfs, Mode
from simulation.TimeUnit import TimeUnit


# Make package/renaming with __init__ file

class LinkingStrategy(ABC):
    """
    The linking strategy determines how the new IPARO is to be linked. The IPARO
    object is first linked using the linking strategy, created (with the links),
    and then finally stored. It depends on the implementation of the IPNS and the IPFS.
    """

    @abstractmethod
    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        """
        Gets the candidate nodes from the latest link, the latest IPARO, and the first link.
        :param latest_link: The link to the latest node.
        :param latest_iparo: The latest IPARO object.
        :param first_link: The link to the first node if it is directly linked to the latest node, None otherwise.
        :returns: The set of candidate links that will be stored in the newly created IPARO.
        """
        pass

    @abstractmethod
    def __str__(self):
        """
        The name of the linking strategy, used for simulations.
        """
        pass


class SingleStrategy(LinkingStrategy):

    def __str__(self):
        return "Single"

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        return {latest_link}


class ComprehensiveStrategy(LinkingStrategy):

    def __str__(self):
        return "Comprehensive"

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        latest_node_links = latest_iparo.linked_iparos.copy()
        latest_node_links.add(latest_link)

        return latest_node_links


class KPreviousStrategy(LinkingStrategy):
    def __init__(self, k: int):
        self.k = k

    def __str__(self):
        return f"{self.k}-Previous"

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        linked_iparos = latest_iparo.linked_iparos.copy()
        linked_iparos.add(latest_link)
        seq_num_to_drop = max(latest_link.seq_num - self.k, 0)
        if seq_num_to_drop > 0:
            iparo_link_to_drop = ipfs.retrieve_nth_iparo(seq_num_to_drop, latest_link)
            linked_iparos.remove(iparo_link_to_drop)
        return linked_iparos


class PreviousStrategy(KPreviousStrategy):

    def __init__(self):
        super().__init__(1)

    def __str__(self):
        return "Previous"


class KRandomStrategy(LinkingStrategy):

    def __init__(self, k: int):
        self.k = k

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        latest_node_links = latest_iparo.linked_iparos
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

    def __str__(self):
        return f"{self.k}-Random"


class SequentialExponentialStrategy(LinkingStrategy):

    def __init__(self, k: float):
        self.k = k

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        node_num = latest_link.seq_num
        indices: set[int] = {0, node_num}
        index = 1.0
        while index < node_num + 1:
            indices.add(node_num - floor(index - 1))
            index *= self.k
        links = IPAROLinkFactory.from_indices(latest_link, indices)
        return links

    def __str__(self):
        return f"Base-{self.k} Sequential Exponential"


class SequentialUniformNPriorStrategy(LinkingStrategy):

    def __init__(self, n: int):
        self.n = n

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        indices: set[int] = {latest_iparo.seq_num * i // (self.n + 1) for i in range(self.n + 2)}
        return IPAROLinkFactory.from_indices(latest_link, indices)

    def __str__(self):
        return f"Sequential Uniform {self.n}-Prior"


class SequentialSMaxGapStrategy(LinkingStrategy):

    # s: the number of hops allowed between linked nodes.
    def __init__(self, s: int):
        self.s = s

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        # Sequentially add nodes with no more than S hops between them
        start_seq_num = latest_link.seq_num - self.s

        # It turns out you can use the previous link to retrieve S-max-gap
        if start_seq_num >= 0:
            prev_link = ipfs.retrieve_nth_iparo(start_seq_num + 1, latest_link)
            prev_iparo = ipfs.retrieve(prev_link.cid)
            # Add 0 to the node indices.
            links = prev_iparo.linked_iparos.copy()
        else:
            links = set()
        links.add(first_link)
        links.add(latest_link)

        return links

    def __str__(self):
        return f"Sequential {self.s}-Max-Gap"


class TemporallyUniformStrategy(LinkingStrategy):
    def __init__(self, n: int):
        self.n = n  # Number of uniformly distributed links to create

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        time_window = latest_link.timestamp - first_link.timestamp
        # Adds nodes sequenced as 1, 2, ..., n-1
        timestamps = {int(first_link.timestamp + i * time_window / self.n) for i in range(1, self.n)}

        # from_timestamps(timestamps: set[int], known_links: set[IPAROLink])
        links, _ = IPAROLinkFactory.from_timestamps(timestamps, {first_link, latest_link})

        # Add latest and first links.
        links.add(first_link)
        links.add(latest_link)

        return links

    def __str__(self):
        return f"Temporally Uniform ({self.n} Nodes)"


class TemporallyMinGapStrategy(LinkingStrategy):
    def __init__(self, min_gap: float):
        """
        :param min_gap: the minimum gap in terms of seconds.
        """
        self.min_gap = min_gap

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        curr_link = latest_link
        current_time = latest_link.timestamp
        known_links = {first_link, latest_link}

        links = set()
        # Keep stepping back using max_gap (Earliest?)
        # Example: * * - * - - - - * * - - * *
        # * = capture, - = no capture
        while curr_link.seq_num > 0:
            current_time = current_time - self.min_gap * TimeUnit.SECONDS
            # Choose earliest after...
            candidate_link, known_links = ipfs.retrieve_closest_iparo(curr_link, known_links,
                                                                      current_time, Mode.EARLIEST_AFTER)

            # but with one exception: if there is no link within that window (i.e. the earliest after
            # mode returns the current link), then we extend the window.
            if curr_link == candidate_link:
                candidate_link, known_links = ipfs.retrieve_closest_iparo(curr_link, known_links,
                                                                          current_time, Mode.LATEST_BEFORE)
            links.add(candidate_link)
            curr_link = candidate_link

        links.add(first_link)
        links.add(latest_link)
        return links

    def __str__(self):
        return f"Temporally Min Gap ({self.min_gap} Seconds)"


class TemporallyExponentialStrategy(LinkingStrategy):
    def __init__(self, base: float, time_unit: int):
        self.base = base
        self.time_unit = time_unit

    def get_candidate_nodes(self, latest_link: IPAROLink, latest_iparo: IPARO, first_link: IPAROLink) -> set[IPAROLink]:
        # Exponential time gaps - assume number of nodes >= 1
        gap = self.time_unit
        time_window = latest_iparo.timestamp - first_link.timestamp
        gaps = []
        while gap < time_window:
            gaps.append(-gap)
            gap *= self.base
        gaps.reverse()

        timestamps = {latest_iparo.timestamp + gap for gap in gaps}
        links, _ = IPAROLinkFactory.from_timestamps(timestamps, {first_link, latest_link})
        links.add(first_link)
        links.add(latest_link)

        return links

    def __str__(self):
        return f"Temporally Exponential ({self.time_unit} Second(s), Base {self.base})"
