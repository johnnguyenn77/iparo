from typing import Optional

from src.system.IPARO import IPARO
from src.system.IPAROLink import IPAROLink
# from src.system.IPFS import IPFS


class IPAROLinkFactory:
    """
    A collection of helper methods dealing with creating IPAROLinks
    """
    def __init__(self):
        pass

    # @classmethod
    # def from_cid(cls, cid: str) -> Optional[IPAROLink]:
    #     """
    #     A helper method that takes in a CID and outputs an IPAROLink (or None if there is no such IPARO)
    #     :param cid: The CID of the IPARO.
    #     :return: The link to the IPARO if the CID is present.
    #     """
    #     iparo = IPFS.retrieve(cid)
    #     if iparo is None:
    #         return None
    #     return IPAROLink(seq_num=iparo.seq_num, timestamp=iparo.timestamp, cid=cid)

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

    # @classmethod
    # def from_indices(cls, link: IPAROLink, indices: set[int]) -> set[IPAROLink]:
    #     """
    #     A helper method that allows the IPFS to retrieve the selected versions of a URL,
    #     using the latest node.
    #     """
    #     sorted_indices = sorted(indices, reverse=True)
    #     curr_link = link
    #     links = set()
    #     for index in sorted_indices:
    #         curr_link = IPFS.retrieve_nth_iparo(index, curr_link)
    #         links.add(curr_link)
    #
    #     return links
