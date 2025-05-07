from system.IPARO import IPARO
from system.IPNS import IPNS
from system.IPFS import IPFS

def get_all_snapshots_for_url(url: str, ipns: IPNS, ipfs: IPFS, ipns_records: dict) -> list[IPARO]:
    peer_id = ipns_records.get(url)
    if not peer_id:
        raise ValueError("This website has not been archived")

    start_cid = ipns.resolve_cid(peer_id)
    visited = set()
    snapshots = []

    def dfs(cid):
        if cid in visited:
            return
        visited.add(cid)

        iparo = ipfs.retrieve(cid)
        snapshots.append(iparo)

        for link in iparo.linked_iparos:
            dfs(link.cid)

    dfs(start_cid)
    return sorted(snapshots, key=lambda x: x.seq_num)
