from datetime import datetime
from typing import Optional

from iparo.IPARO import IPARO
from iparo.IPAROLink import IPAROLink
from iparo.IPFS import ipfs
from iparo.IPNS import ipns


class IPAROLinkFactory:
    """
    A collection of helper methods dealing with creating IPAROLinks
    """
    def __init__(self):
        pass

    @classmethod
    def from_cid(cls, cid: str) -> Optional[IPAROLink]:
        """
        A helper method that takes in a CID and outputs an IPAROLink (or None if there is no such IPARO)
        :param cid: The CID of the IPARO.
        :return: The link to the IPARO if the CID is present.
        """
        iparo = ipfs.retrieve(cid)
        if iparo is None:
            return None
        return IPAROLink(seq_num=iparo.seq_num, timestamp=iparo.timestamp, cid=cid)

    @classmethod
    def from_cid_iparo(cls, cid: str, iparo: IPARO) -> IPAROLink:
        """
        A helper method that takes in a CID and the corresponding IPARO object, and
        outputs an IPAROLink. The assumption underlying the operation is that the
        IPARO's CID maps directly to the IPARO object. This will save an IPFS
        operation each time the method is called, and it does not require a check
        for ``None``.

        :param iparo: The IPARO object itself.
        :param cid: The CID of the IPARO.
        :return: The link to the IPARO
        """
        return IPAROLink(seq_num=iparo.seq_num, timestamp=iparo.timestamp, cid=cid)

    @classmethod
    def from_indices(cls, link: IPAROLink, indices: set[int]) -> set[IPAROLink]:
        """
        A helper method that allows the IPFS to retrieve the selected versions of a URL,
        using the latest node.
        """
        sorted_indices = sorted(indices, reverse=True)
        curr_link = link
        links = set()
        for index in sorted_indices:
            curr_link = ipfs.retrieve_nth_iparo(index, curr_link)
            links.add(curr_link)

        return links

    @classmethod
    def from_timestamps(cls, link: IPAROLink, known_links: set[IPAROLink], timestamps: set[str]) -> tuple[set[IPAROLink], set[IPAROLink]]:
        """
        Constructs a list of IPARO links from a set of timestamps.
        """
        # Question: Would timestamps be set[str] or should it be left as set[datetime]?
        sorted_timestamps = sorted(timestamps, reverse=True)
        links = set()
        for ts in sorted_timestamps:
            # Question: Should I just add one known link for each time I iterate through?
            # Or should I just add all the IPARO's links in the list?
            known_links.add(link)
            link, known_links = ipfs.retrieve_closest_iparo(link, known_links, ts)
            links.add(link)

        return links, known_links

    @classmethod
    def get_links_to_first_and_latest_nodes(self, url) -> tuple[IPAROLink, IPAROLink, IPARO]:
        """
        A helper method that adds the first and latest links.
        """
        latest_cid = ipns.get_latest_cid(url)
        latest_iparo = ipfs.retrieve(latest_cid)
        latest_link = IPAROLink(seq_num=latest_iparo.seq_num, timestamp=latest_iparo.timestamp, cid=latest_cid)
        first_link = ipfs.retrieve_nth_iparo(0, latest_link)
        return first_link, latest_link, latest_iparo

    @classmethod
    def get_link_to_latest_node(self, url) -> tuple[IPAROLink, IPARO]:
        """
        A helper method that adds the first and latest links.
        """
        latest_cid = ipns.get_latest_cid(url)
        latest_iparo = ipfs.retrieve(latest_cid)
        latest_link = IPAROLink(seq_num=latest_iparo.seq_num, timestamp=latest_iparo.timestamp, cid=latest_cid)
        return latest_link, latest_iparo

    @classmethod
    def get_latest_node_links(self, url) -> tuple[set[IPAROLink], IPAROLink, IPARO]:
        """
        A helper method to get the latest link as well as the set of all IPARO links for the latest node.
        """
        latest_cid = ipns.get_latest_cid(url)
        latest_iparo = ipfs.retrieve(latest_cid)
        linked_iparos = latest_iparo.linked_iparos
        latest_iparo_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_iparo)
        linked_iparos.add(latest_iparo_link)

        return linked_iparos, latest_iparo_link, latest_iparo



