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
                 version_volume: VersionVolume):
        self.linking_strategy = linking_strategy
        self.version_density = version_density
        self.version_volume = version_volume

        # Debug variables for testing.
        self.ipfs_store_results: dict[str, int] = dict()
        self.ipns_store_results: dict[str, int] = dict()
        self.ipfs_retrieve_results: dict[str, int] = dict()
        self.ipns_retrieve_results: dict[str, int] = dict()

    def run(self, k: int, verbose=True):
        """
        Sets up the testing environment for an IPARO simulation, and then
        performs k random.
        """
        nodes = self.version_density.get_iparos(self.version_volume)
        # Link the IPAROs in the IPFS
        for i, node in enumerate(nodes):
            node.seq_num = i
            try:
                node.linked_iparos = self.linking_strategy.get_candidate_nodes(URL)
            except:
                node.linked_iparos = set()
            cid = ipfs.store(node)
            ipns.update(URL, cid)

        self.ipfs_store_results = ipfs.get_counts()
        self.ipns_store_results = ipns.get_counts()
        if verbose:
            IPAROSimulation.print_counts("Store")
        IPAROSimulation.reset()

        # Get node number from latest CID
        latest_cid = ipns.get_latest_cid(URL)
        latest_node = ipfs.retrieve(latest_cid)
        for i in range(k):
            selected_index = random.randint(0, latest_node.seq_num - 1)
            ipfs.retrieve_by_number(URL, selected_index)

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
        for cid in ipfs.get_all_cids(URL):
            iparo = ipfs.retrieve(cid)
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
