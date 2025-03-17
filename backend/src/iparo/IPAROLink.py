from dataclasses import dataclass


@dataclass(frozen=True)
class IPAROLink:
    """
    Defines the IPARO Link class that has a sequence number, a datetime, and a CID.
    """
    seq_num: int
    timestamp: str
    cid: str
