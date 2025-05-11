from system.IPARO import IPARO
from system.IPNS import IPNS
from system.IPFS import IPFS

def get_all_snapshots_for_url(url: str, ipns: IPNS, ipfs: IPFS, ipns_records: dict) -> dict[str, IPARO]:
    peer_id = ipns_records.get(url)
    if not peer_id:
        raise ValueError("This website has not been archived")

    start_cid = ipns.resolve_cid(peer_id)
    visited = set()
    snapshots = {}

    def get_all_cids(cid):
        if cid in visited:
            return
        visited.add(cid)

        iparo = ipfs.retrieve(cid)
        snapshots[cid] = iparo

        for link in iparo.linked_iparos:
            get_all_cids(link.cid)

    get_all_cids(start_cid)

    return dict(sorted(snapshots.items(), key=lambda item: item[1].seq_num))