from datetime import datetime, timedelta

from system.IPARO import IPARO
from system.IPAROLink import IPAROLink
from system.IPAROLinkFactory import IPAROLinkFactory
from system.IPFS import IPFS, Mode
from system.IPNS import IPNS

def check_latest_cid(url: str, ipns: IPNS, ipfs: IPFS, ipns_records: dict) -> tuple[IPAROLink, IPARO]:
    """Checks the archival status and if it is not archived, throws a ValueError."""
    peer_id = ipns_records.get(url)
    if not peer_id:
        raise ValueError("This website has not been archived")

    # W
    latest_cid = ipns.resolve_cid(peer_id)
    latest_iparo = ipfs.retrieve(latest_cid)
    latest_link = IPAROLinkFactory.from_cid_iparo(latest_cid, latest_iparo)

    return latest_link, latest_iparo


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

def retrieve_by_number(url: str, ipns: IPNS, ipfs: IPFS, num: int, ipns_records: dict) -> dict[str, IPARO]:
    """
    Returns a JSON object that retrieves an IPARO by sequence number.
    """
    latest_link, latest_iparo = check_latest_cid(url, ipns, ipfs, ipns_records)
    link, iparo = ipfs.retrieve_by_number(latest_link, num)
    return {link.cid: iparo}


def retrieve_closest_iparos(url: str, ipns: IPNS, ipfs: IPFS, date: str, ipns_records: dict, limit: int) -> dict[str, IPARO]:
    """
    Returns a JSON object that retrieves all IPARO objects on a specific date, up to limit. This method
    will return the closest IPARO, plus N IPAROs that are sequentially . The date is a string that contains
    the specific date in YYYY-mm-dd format.
    """
    latest_link, _ = check_latest_cid(url, ipns, ipfs, ipns_records)

    timestamp = datetime.strptime("%Y-%m-%d", date)

    # We want all the known links for the closest timestamp,
    # so we don't have to travel all the way back.
    link, iparo, known_links = ipfs.retrieve_by_date(latest_link, date, Mode.CLOSEST)
    iparos = ipfs.retrieve_closest_iparos(iparo, latest_link, known_links, limit)

    return iparos