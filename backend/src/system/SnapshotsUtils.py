from datetime import datetime

from system.IPARO import IPARO
from system.IPFS import IPFS, Mode
from system.IPNS import IPNS


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


def get_latest_cid(url: str, ipns: IPNS, ipns_records: dict[str, str]):
    """Gets the latest CID of a URL"""
    peer_id = ipns_records.get(url)
    latest_cid = ipns.resolve_cid(peer_id)
    return latest_cid


def retrieve_by_number(url: str, ipns: IPNS, ipfs: IPFS, num: int, ipns_records: dict) -> dict[str, IPARO]:
    """
    Returns a JSON object that retrieves an IPARO by sequence number.
    """

    latest_cid = get_latest_cid(url, ipns, ipns_records)
    link, iparo = ipfs.retrieve_by_number(latest_cid, num)
    return {link.cid: iparo}


def retrieve_closest_iparos(url: str, ipns: IPNS, ipfs: IPFS, date: str, ipns_records: dict, limit: int) -> dict[
    str, IPARO]:
    """
    Returns a JSON object that retrieves all IPARO objects on a specific date, up to limit. This method
    will return the closest IPARO, plus N IPAROs that are closest sequentially. The date is a string that
    contains the specific date in YYYY-mm-dd format.
    """
    peer_id = ipns_records.get(url)
    latest_cid = ipns.resolve_cid(peer_id)

    # Need to convert the YYYY-mm-dd into timestamp
    timestamp = datetime.strptime(date, "%Y-%m-%d").isoformat()

    # And convert timestamp into string. (Python uses +00:00 instead of Z as suffix, so I had to change it).
    time_string = timestamp.replace("+00:00", "Z")

    # We want all the known links for the closest timestamp,
    # so we don't have to travel all the way back.
    iparo, known_links = ipfs.retrieve_by_date(latest_cid, time_string, Mode.CLOSEST)

    iparos = ipfs.retrieve_closest_iparos(iparo, latest_cid, known_links, limit)

    return iparos
