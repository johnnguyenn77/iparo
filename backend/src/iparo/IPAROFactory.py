from datetime import datetime

from iparo.IPAROException import IPARONotFoundException
from iparo.IPARO import IPARO
from iparo.IPARODateFormat import IPARODateFormat
from iparo.IPFS import ipfs
from iparo.IPNS import ipns


class IPAROFactory:
    @classmethod
    def create_node(cls, url: str, content: bytes) -> IPARO:
        timestamp = datetime.strftime(datetime.now(), IPARODateFormat.DATE_FORMAT)
        try:
            latest_node = ipfs.retrieve(ipns.get_latest_cid(url))
            seq_num = latest_node.seq_num + 1 if latest_node is not None else 0
        except IPARONotFoundException:
            seq_num = 0
        iparo = IPARO(url=url, content=content, timestamp=timestamp,
                      linked_iparos=set(), seq_num=seq_num)
        return iparo