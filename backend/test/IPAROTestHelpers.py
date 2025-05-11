from simulation import IPARO
from IPAROTestConstants import *
from simulation.IPFS import *
from simulation.LinkingStrategy import *
from simulation.TimeUnit import TimeUnit


def add_nodes(num_nodes: int):
    iparos = []
    for i in range(num_nodes):
        content = generate_random_content_string()
        try:
            strategy = SingleStrategy()
            first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
            linked_iparos = strategy.get_candidate_nodes(latest_link, latest_iparo, first_link)
            # todo add specific exception.
        except IPARONotFoundException:
            linked_iparos = set()
        timestamp = time1 + 10 * i * TimeUnit.SECONDS
        iparo = IPARO(content=content, timestamp=timestamp,
                      url=URL, linked_iparos=linked_iparos, seq_num=i)
        iparos.append(iparo)
        cid, _ = ipfs.store(iparo)

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
            first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
            linked_iparos = strategy.get_candidate_nodes(latest_link, latest_iparo, first_link)
        except IPARONotFoundException:
            linked_iparos = set()
        lengths.append(len(linked_iparos))
        timestamp = time1 + i * TimeUnit.SECONDS
        iparo = IPARO(content=content, timestamp=timestamp,
                      url=URL, linked_iparos=linked_iparos, seq_num=i)
        cid, _ = ipfs.store(iparo)
        ipns.update(URL, cid)
    return lengths


def test_strategy_verbose(strategy: LinkingStrategy) -> tuple[list[int], list[str], list[IPARO]]:
    lengths = []
    cids = []
    iparos = []
    for i in range(100):
        content = generate_random_content_string()
        try:
            first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
            linked_iparos = strategy.get_candidate_nodes(latest_link, latest_iparo, first_link)
        except IPARONotFoundException:
            linked_iparos = set()
        timestamp = time1 + i * TimeUnit.SECONDS
        iparo = IPARO(content=content, timestamp=timestamp, url=URL, linked_iparos=linked_iparos, seq_num=i)
        cid, _ = ipfs.store(iparo)
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
        try:
            first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
            linked_iparos = strategy.get_candidate_nodes(latest_link, latest_iparo, first_link)
        except IPARONotFoundException:
            linked_iparos = set()

        iparo = IPARO(url=URL, content=content, linked_iparos=linked_iparos, timestamp=timestamp, seq_num=i)
        cid, _ = ipfs.store(iparo)
        ipns.update(URL, cid)

    # Where would the next link go?

    first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
    links = strategy.get_candidate_nodes(latest_link, latest_iparo, first_link)

    return sorted([int((link.timestamp - time1) / TimeUnit.SECONDS) for link in links])


def test_closest_iparo(rel_time: float):
    """
    Helper method for testing what the closest IPARO is to the given relative time.

    :param rel_time: The number of seconds, relative to the link timestamp.
    """
    first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
    timestamp = int(latest_link.timestamp + rel_time * TimeUnit.SECONDS)
    observed_iparo, _ = ipfs.retrieve_closest_iparo(latest_link, {latest_link, first_link}, timestamp)

    return observed_iparo.seq_num
