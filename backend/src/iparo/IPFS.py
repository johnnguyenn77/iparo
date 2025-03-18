import hashlib
import pickle
from datetime import datetime
from enum import Enum

from iparo.Exceptions import IPARONotFoundException
from iparo.IPARO import IPARO
from iparo.IPARODateConverter import IPARODateConverter
from iparo.IPAROLink import IPAROLink
from iparo.IPNS import ipns


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

    def store(self, iparo: IPARO) -> str:
        """
        Stores a node with its CID.

        Args:
            iparo (IPARO): The IPARO object to store.

        Returns:
            The CID of the newly stored IPARO.
        """
        iparo_bytes = pickle.dumps(iparo)
        sha256_hash = hashlib.sha256(iparo_bytes).hexdigest()
        cid = 'Qm' + sha256_hash[:34]
        self.store_count += 1
        self.data[cid] = iparo_bytes
        return cid

    def reset_data(self):
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

    def retrieve_by_url_and_timestamp(self, url: str, target_timestamp: datetime, mode: Mode = Mode.LATEST_BEFORE) -> \
            IPAROLink:
        link = self.get_latest_link(url)
        return self.retrieve_closest_iparo(link, target_timestamp, mode)

    def retrieve_nth_iparo(self, link: IPAROLink, number: int) -> IPAROLink:
        """
        A helper method that enables the retrieval of IPARO using a sequence number
        to save IPARO operations by adding the ability to repeatedly apply the
        greedy search method.
        """
        if link.seq_num < number:
            raise IPARONotFoundException(number)
        elif link.seq_num == number:
            return link

        # It is assumed that there is a link to the previous node.
        iparo = self.retrieve(link.cid)
        candidate_links = [link for link in iparo.linked_iparos if link.seq_num >= number]
        if not candidate_links:
            raise IPARONotFoundException(number)
        next_link = min(candidate_links, key=lambda link: link.seq_num)

        return self.retrieve_nth_iparo(next_link, number)

    def retrieve_closest_iparo(self, link: IPAROLink, timestamp: datetime, mode: Mode = Mode.CLOSEST) -> IPAROLink:
        """
        A helper method that enables the retrieval of IPARO using a sequence number
        to save IPARO operations by adding the ability to repeatedly apply the
        greedy search method from an IPARO link. Unlike the other method, it only applies
        the closest IPARO.
        """
        curr_ts = IPARODateConverter.str_to_datetime(link.timestamp)

        try:
            if curr_ts == timestamp:
                return link
            prev_link = self.retrieve_nth_iparo(link, link.seq_num - 1)
            prev_ts = IPARODateConverter.str_to_datetime(prev_link.timestamp)
            # Calculate time fraction.
            time_frac = (timestamp - prev_ts) / (curr_ts - prev_ts)
            if time_frac > 1:
                raise IPARONotFoundException("Not a valid timestamp")
            elif time_frac >= 0:
                if mode == Mode.CLOSEST:
                    return prev_link if time_frac <= 0.5 else link
                elif mode == Mode.EARLIEST_AFTER:
                    return link if time_frac > 0 else prev_link
                return prev_link if time_frac < 1 else link
            else:
                iparo = self.retrieve(prev_link.cid)
                candidate_links = iparo.linked_iparos
                candidate_links.add(prev_link)
                # Find minimum time
                next_link = min([link for link in candidate_links if
                                 IPARODateConverter.str_to_datetime(link.timestamp) >= timestamp],
                                key=lambda link: IPARODateConverter.str_to_datetime(link.timestamp))
                return self.retrieve_closest_iparo(next_link, timestamp, mode)
        except IPARONotFoundException as e:
            raise e
        except ValueError:
            raise IPARONotFoundException("No previous link")

    def retrieve_iparo_by_url_and_number(self, url: str, number: int) -> IPAROLink:
        """
        Retrieves the IPARO CID corresponding to a given sequence number and a URL.
        Usually only used for tests.
        """
        cid = ipns.get_latest_cid(url)

        # To avoid a circular dependency on IPAROLinkFactory
        iparo = self.retrieve(cid)
        link = IPAROLink(cid=cid, seq_num=iparo.seq_num, timestamp=iparo.timestamp)
        result = self.retrieve_nth_iparo(link, number)
        return result

    def get_counts(self) -> dict:
        """
        Returns the number of store, and retrieve operations performed.

        Returns:
            dict: Dictionary with counts of store, and retrieve operations.
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
            link = self.get_latest_link(url)
            while True:
                links.append(link)
                link = self.retrieve_nth_iparo(link, link.seq_num - 1)
        finally:
            return links

    def get_latest_link(self, url: str) -> IPAROLink:
        cid = ipns.get_latest_cid(url)
        iparo = self.retrieve(cid)
        return IPAROLink(cid=cid, seq_num=iparo.seq_num, timestamp=iparo.timestamp)

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
