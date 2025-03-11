from LinkingStrategy import *

# Use networkx and pyvis.network
import networkx as nx
from pyvis.network import Network

from VersionDensity import *
from IPFS import ipfs


def print_counts(header: str):
    print(header)
    print("IPFS Counts:")
    print(ipfs.get_counts())
    print("IPNS Counts:")
    print(ipns.get_counts())


class IPAROSimulation:

    @classmethod
    def setup(cls, linking_strategy: LinkingStrategy, version_density: VersionDensity,
                 version_volume: VersionVolume):
        nodes = version_density.get_iparos(version_volume)
        # Link the IPAROs in the IPFS
        for i, node in enumerate(nodes):
            node.seq_num = i
            node.linked_iparos = linking_strategy.get_candidate_nodes(URL)
            cid = ipfs.store(node)
            ipns.update(URL, cid)

        print_counts("Store")
        ipfs.reset_counts()
        ipns.reset_counts()

    @classmethod
    def run(cls, k: int):
        """
        Run the simulation by performing k uniform random retrievals.
        """

        # Get node number from latest CID
        latest_cid = ipns.get_latest_cid(URL)
        latest_node = ipfs.retrieve(latest_cid)
        for i in range(k):
            selected_index = random.randint(0, latest_node.seq_num - 1)
            ipfs.retrieve_by_number(URL, selected_index)

        print_counts("Retrieve")

    @classmethod
    def as_graph(cls):
        """
        Creates a DiGraph object.
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

