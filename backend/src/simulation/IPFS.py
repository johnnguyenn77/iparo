import gc
import hashlib
import pickle
from enum import Enum

from src.simulation.IPAROException import IPARONotFoundException
from src.simulation.IPARO import IPARO
from src.simulation.IPAROLink import IPAROLink
from src.simulation.IPNS import ipns


class Mode(Enum):
    LATEST_BEFORE = 0,
    CLOSEST = 1,
    EARLIEST_AFTER = 2


class IPFS:
    """
    The InterPlanetary File System is responsible for hashing, storing,
    retrieving, and linking IPARO objects.
    """

    def __init__(self):
        self.data: dict[str, bytes] = {}
        self.retrieve_count = 0
        self.store_count = 0

    def store(self, iparo: IPARO) -> tuple[str, bytes]:
        """
        Stores a node with its CID.

        Args:
            iparo (IPARO): The IPARO object to store.

        Returns:
            The tuple containing the CID of the newly stored IPARO as the
            first element and the serialized IPARO as the second element.
        """
        iparo_bytes = pickle.dumps(iparo)
        sha256_hash = hashlib.sha256(iparo_bytes).hexdigest()
        cid = 'Qm' + sha256_hash[:34]
        self.store_count += 1
        self.data[cid] = iparo_bytes
        return cid, iparo_bytes

    def reset_data(self):
        del self.data
        gc.collect()
        self.data: dict[str, IPARO] = {}

    def retrieve(self, cid) -> IPARO:
        """
        Retrieves the IPARO object corresponding to a given CID, if it exists;
        otherwise, it throws an IPARONotFoundException.
        """
        self.retrieve_count += 1
        if cid not in self.data:
            raise IPARONotFoundException(cid)
        iparo_bytes = self.data[cid]
        return pickle.loads(iparo_bytes)

    def get_link_to_latest_node(self, url: str) -> tuple[IPAROLink, IPARO]:
        """
        A method that fetches the latest link and the latest IPARO.
        """
        latest_cid = ipns.get_latest_cid(url)
        latest_iparo = self.retrieve(latest_cid)
        latest_link = IPAROLink(seq_num=latest_iparo.seq_num, timestamp=latest_iparo.timestamp, cid=latest_cid)
        return latest_link, latest_iparo

    def get_links_to_first_and_latest_nodes(self, url: str) -> tuple[IPAROLink, IPAROLink, IPARO]:
        """
        A helper method that adds the latest link and the first link, where the first link is "quickly"
        searched for in constant time (in other words, it finds the first link if and only if it is already
        in the list of linked IPAROs from the latest IPARO).
        :param url: The URL
        :returns: The tuple consisting of the first link, the latest link, and the latest IPARO, in that order.
        """
        latest_cid = ipns.get_latest_cid(url)
        latest_iparo = self.retrieve(latest_cid)
        latest_link = IPAROLink(seq_num=latest_iparo.seq_num, timestamp=latest_iparo.timestamp, cid=latest_cid)
        candidate_links = [link for link in latest_iparo.linked_iparos if link.seq_num == 0]
        first_link = candidate_links[0] if candidate_links else None
        if latest_link.seq_num == 0:
            first_link = latest_link
        return first_link, latest_link, latest_iparo

    def retrieve_nth_iparo(self, number: int, link: IPAROLink) -> IPAROLink:
        """
        A method that enables the retrieval of IPARO using a sequence number
        to save IPARO operations by adding the ability to repeatedly apply the
        greedy search method. For bulk retrieval, use the IPAROLinkFactory.
        """
        # It is assumed that there is a link to the previous node.
        if link.seq_num < number:
            raise IPARONotFoundException(number)

        curr_link = link
        while curr_link.seq_num != number:
            iparo = self.retrieve(curr_link.cid)
            candidate_links = [link for link in iparo.linked_iparos if link.seq_num >= number]
            if not candidate_links:
                raise IPARONotFoundException(number)
            next_link = min(candidate_links, key=lambda link: link.seq_num)
            curr_link = next_link

        return curr_link

    def retrieve_closest_iparo(self, curr_link: IPAROLink, known_links: set[IPAROLink], timestamp: int,
                               mode: Mode = Mode.CLOSEST) \
            -> tuple[IPAROLink, set[IPAROLink]]:
        """
        A helper method that enables the retrieval of IPARO using a sequence number
        to save IPARO operations by adding the ability to repeatedly apply the
        greedy search method from an IPARO link. Unlike the other method, it only applies
        the closest IPARO.
        """
        while True:
            curr_ts = curr_link.timestamp
            if curr_ts == timestamp or curr_link.seq_num == 0:
                return curr_link, known_links
            prev_link = self.retrieve_nth_iparo(curr_link.seq_num - 1, curr_link)
            prev_ts = prev_link.timestamp
            # Calculate time fraction.
            if curr_ts != prev_ts:
                time_frac = (timestamp - prev_ts) / (curr_ts - prev_ts)
                if time_frac >= 0:
                    if mode == Mode.CLOSEST:
                        chosen_link = prev_link if time_frac <= 0.5 else curr_link
                    elif mode == Mode.EARLIEST_AFTER:
                        chosen_link = curr_link if time_frac > 0 else prev_link
                    else:
                        chosen_link = prev_link if time_frac < 1 else curr_link
                    return chosen_link, known_links

            # Go over known links...
            iparo = self.retrieve(prev_link.cid)

            candidate_links = {link for link in iparo.linked_iparos if link.timestamp >= timestamp}
            candidate_links.add(prev_link)

            known_links.update(candidate_links)

            # Find minimum time greater than the timestamp.
            next_link = min(candidate_links, key=lambda link: (link.timestamp, link.seq_num))
            curr_link = next_link

    def retrieve_iparo_by_url_and_number(self, url: str, number: int) -> IPAROLink:
        """
        Retrieves the IPARO CID corresponding to a given sequence number and a URL.
        """
        link, iparo = self.get_link_to_latest_node(url)
        result = self.retrieve_nth_iparo(number, link)
        return result

    def retrieve_iparo_by_url_and_timestamp(self, url: str, timestamp: int, mode: Mode = Mode.CLOSEST) -> IPAROLink:
        """
        Retrieves the IPARO given a URL and a timestamp, according to a given mode, using
        a greedy search method. For bulk retrieval, use ``IPAROLinkFactory.from_timestamps``.

        :param url: The URL.
        :param timestamp: The timestamp.
        :param mode: The mode by which we find the IPARO.
        """
        latest_link, latest_iparo = self.get_link_to_latest_node(url)
        link, _ = self.retrieve_closest_iparo(latest_link, {latest_link}, timestamp, mode)
        return link

    def get_counts(self) -> dict:
        """
        Returns the number of store and retrieve operations performed.

        Returns:
            dict: Dictionary with counts of store and retrieve operations.
        """
        counts = {"store": self.store_count, "retrieve": self.retrieve_count}
        return counts

    def reset_counts(self):
        """
        Resets the operation counters.
        """
        self.store_count = 0
        self.retrieve_count = 0

    def get_all_links(self, url: str) -> list[IPAROLink]:
        """
        Retrieves the list of all links in the IPFS, corresponding to the given URL.
        The links are sorted from latest to earliest. This will also include all the CIDs.
        """
        links = []
        try:
            link, _ = self.get_link_to_latest_node(url)
            while True:
                links.append(link)
                link = self.retrieve_nth_iparo(link.seq_num - 1, link)
        finally:
            return links

    def get_all_iparos(self, url: str) -> list[IPARO]:
        """
        Retrieves the list of all IPAROs in the IPFS, corresponding to the given URL.
        The nodes are sorted from latest to earliest. This will also include all the CIDs.
        """
        iparos = []
        try:
            cid = ipns.get_latest_cid(url)
            while True:
                iparo = self.retrieve(cid)
                iparos.append(iparo)

                links = [link for link in iparo.linked_iparos if link.seq_num == iparo.seq_num - 1]
                if len(links) == 0:
                    raise IPARONotFoundException()
                cid = links[0].cid
        finally:
            return iparos


ipfs = IPFS()
