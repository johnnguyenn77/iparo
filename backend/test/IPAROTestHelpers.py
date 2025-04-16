import datetime

from iparo import IPARO
from IPAROTestConstants import *
from iparo.IPFS import *
from iparo.LinkingStrategy import *
from iparo.TimeUnit import TimeUnit


def add_nodes(num_nodes: int):
    iparos = []
    for i in range(num_nodes):
        content = generate_random_content_string()
        try:
            linked_iparos = SingleStrategy().get_candidate_nodes(URL)
            # todo add specific exception.
        except Exception:
            linked_iparos = set()
        timestamp = time1 + 10 * i * TimeUnit.SECONDS
        iparo = IPARO(content=content, timestamp=timestamp,
                      url=URL, linked_iparos=linked_iparos, seq_num=i)
        iparos.append(iparo)
        cid = ipfs.store(iparo)

        ipns.update(URL, cid)
    return iparos


def generate_random_content_string() -> bytes:
    # Contains all printable characters in the original ASCII format, which are represented by codes from 32 to 126.
    contents = bytes([random.randint(32, 126) for _ in range(100)])
    return contents


def test_strategy(strategy: LinkingStrategy) -> list[int]:
    lengths = []
    for i in range(100):
        content = generate_random_content_string()
        try:
            linked_iparos = strategy.get_candidate_nodes(URL)
        except IPARONotFoundException:
            linked_iparos = set()
        lengths.append(len(linked_iparos))
        timestamp = time1 + i * TimeUnit.SECONDS
        iparo = IPARO(content=content, timestamp=timestamp,
                      url=URL, linked_iparos=linked_iparos, seq_num=i)
        cid = ipfs.store(iparo)
        ipns.update(URL, cid)
    return lengths


def test_strategy_verbose(strategy: LinkingStrategy) -> tuple[list[int], list[str], list[IPARO]]:
    lengths = []
    cids = []
    iparos = []
    for i in range(100):
        content = generate_random_content_string()
        try:
            linked_iparos = strategy.get_candidate_nodes(URL)
        except IPARONotFoundException:
            linked_iparos = set()
        timestamp = time1 + i * TimeUnit.SECONDS
        iparo = IPARO(content=content, timestamp=timestamp, url=URL, linked_iparos=linked_iparos, seq_num=i)
        cid = ipfs.store(iparo)
        ipns.update(URL, cid)
        iparos.append(iparo)
        cids.append(cid)
        lengths.append(len(linked_iparos))
    return lengths, cids, iparos


def test_strategy_with_time_distribution(strategy: LinkingStrategy, relative_times: list[int]) -> list[int]:
    """
    :param strategy: The strategy to test
    :param relative_times: The times relative to the first node in seconds.
    :return: A list of timestamps that are connected to the latest node by the linking strategy.
    """
    for i, dt in enumerate(relative_times):
        content = generate_random_content_string()
        timestamp = int(time1 + dt * TimeUnit.SECONDS)
        iparo = IPARO(url=URL, content=content, linked_iparos=set(), timestamp=timestamp, seq_num=i)
        try:
            iparo.linked_iparos = strategy.get_candidate_nodes(URL)
        except IPARONotFoundException:
            pass
        cid = ipfs.store(iparo)
        ipns.update(URL, cid)

    # Where would the next link go?
    links = strategy.get_candidate_nodes(URL)

    return sorted([int((link.timestamp - time1) / TimeUnit.SECONDS) for link in links])


def test_closest_iparo(rel_time: float):
    """
    Helper method for testing what the closest IPARO is to the given relative time.

    :param rel_time: The number of seconds, relative to the link timestamp.
    """
    cid = ipns.get_latest_cid(URL)
    latest_iparo = ipfs.retrieve(cid)
    link = IPAROLinkFactory.from_cid_iparo(cid, latest_iparo)
    timestamp = int(link.timestamp + rel_time * TimeUnit.SECONDS)
    observed_iparo, _ = ipfs.retrieve_closest_iparo(link, {link}, timestamp)

    return observed_iparo.seq_num
