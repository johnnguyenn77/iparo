from iparo.IPAROException import IPARONotFoundException
from iparo.IPNS import ipns
from iparo.LinkingStrategy import *

import networkx as nx

from iparo.VersionDensity import *
from iparo.IPFS import ipfs
import matplotlib.pyplot as plt


class IPAROSimulation:
    """
    The class for the testing environment.
    """

    def __init__(self, linking_strategy: LinkingStrategy, version_density: VersionDensity,
                 version_volume: VersionVolume, url: str = "example.com"):
        self.linking_strategy = linking_strategy
        self.version_density = version_density
        self.version_volume = version_volume
        self.url = url

        # Debug variables for testing.
        self.ipfs_store_results: dict[str, int] = dict()
        self.ipns_store_results: dict[str, int] = dict()
        self.ipfs_retrieve_results: dict[str, int] = dict()
        self.ipns_retrieve_results: dict[str, int] = dict()

    def run(self, k: int, verbose=True):
        """
        Sets up the testing environment for an IPARO simulation, and then
        performs k random retrievals.
        """
        generator = VersionGenerator(self.version_density)
        nodes = generator.generate(k, self.url)
        # Link the IPAROs in the IPFS
        for i, node in enumerate(nodes):
            if i == 2:
                pass
            node.seq_num = i
            try:
                first_link, latest_link, latest_node = ipfs.get_links_to_first_and_latest_nodes(self.url)
                node.linked_iparos = self.linking_strategy.get_candidate_nodes(latest_link, latest_node, first_link)
            except IPARONotFoundException:
                node.linked_iparos = set()
            cid, _ = ipfs.store(node)
            ipns.update(self.url, cid)

        self.ipfs_store_results = ipfs.get_counts()
        self.ipns_store_results = ipns.get_counts()
        if verbose:
            IPAROSimulation.print_counts("Store")
        IPAROSimulation.reset()

        # Get node number from latest CID
        latest_cid = ipns.get_latest_cid(self.url)
        latest_node = ipfs.retrieve(latest_cid)
        for i in range(k):
            selected_index = random.randint(0, latest_node.seq_num - 1)

            # The intent is to find separate numbers, where the numbers are not known until at runtime.
            ipfs.retrieve_iparo_by_url_and_number(self.url, selected_index)
        if verbose:
            IPAROSimulation.print_counts("Retrieve")

        self.ipfs_retrieve_results = ipfs.get_counts()
        self.ipns_retrieve_results = ipns.get_counts()

    @classmethod
    def print_counts(cls, header: str):
        """
        A tool that can be useful in debugging.
        """
        print(header)
        print("IPFS Counts:")
        print(ipfs.get_counts())
        print("IPNS Counts:")
        print(ipns.get_counts())

    def as_graph(self):
        """
        Creates a DiGraph object out of the current nodes in the IPFS.
        """
        # Do comprehensive
        nx_graph = nx.DiGraph()
        for iparo in ipfs.get_all_iparos(self.url):
            curr_num = iparo.seq_num
            nx_graph.add_node(curr_num)
            for link in iparo.linked_iparos:
                nx_graph.add_edge(curr_num, link.seq_num)

        return nx_graph

    @classmethod
    def reset(cls, reset_data=False):
        """Resets the counts (and optionally, the data) from the IPNS and IPFS."""
        if reset_data:
            ipfs.reset_data()
            ipns.reset_data()
        ipfs.reset_counts()
        ipns.reset_counts()


if __name__ == "__main__":
    linking_strategy = TemporallyUniformStrategy(2)
    simulation = IPAROSimulation(linking_strategy=linking_strategy,
                                 version_volume=VersionVolume.MEDIUM,
                                 version_density=UniformVersionDensity())
    simulation.run(100, verbose=False)
    nx.draw_networkx(simulation.as_graph(), arrows=True)
    plt.show()
