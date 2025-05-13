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
    cid, iparo = ipfs.retrieve_by_number(latest_link, num)
    return {cid: iparo}


def retrieve_by_date(url: str, ipns: IPNS, ipfs: IPFS, date: str, ipns_records: dict) -> dict[str, IPARO]:
    """
    Returns a JSON object that retrieves all IPARO objects for a specific date.
    """
    latest_link, latest_iparo = check_latest_cid(url, ipns, ipfs, ipns_records)

    earliest_time = datetime.strptime("%Y-%m-%d", date)
    latest_timestamp = (earliest_time + timedelta(days=1, microseconds=-1)).isoformat()
    earliest_timestamp = earliest_time.isoformat()

    latest_link, latest_iparo, known_links = ipfs.retrieve_by_date(latest_link, latest_timestamp, Mode.LATEST_BEFORE)
    earliest_link, _, _ = ipfs.retrieve_by_date(latest_link, earliest_timestamp, Mode.EARLIEST_AFTER)
    iparos = ipfs.retrieve_all_iparos_in_range(earliest_link.cid, latest_link, latest_iparo)
    return iparos