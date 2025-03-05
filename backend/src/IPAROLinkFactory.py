from typing import Optional

from IPARO import IPARO
from IPAROLink import IPAROLink
from IPFS import ipfs


class IPAROLinkFactory:
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