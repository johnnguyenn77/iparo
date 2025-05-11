import os

from simulation.IPAROException import IPARONotFoundException
from simulation.IPNS import ipns
from simulation.LinkingStrategy import *

import networkx as nx

from simulation.VersionDensity import *
from simulation.IPFS import ipfs


class IPAROSimulationWriter:
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
        self.num_links = 0

    def run(self, k: int, verbose=True):
        """
        Sets up the testing environment for an IPARO simulation, and then
        performs 100 uniform random date retrievals and 100 uniform random number retrievals.
        """
        print(f"{self.linking_strategy} - {self.version_density} - {self.version_volume}")
        print("Store")
        generator = VersionGenerator(self.version_density)
        nodes = generator.generate(self.version_volume, self.url)
        # Link the IPAROs in the IPFS
        first_node = None
        for i, node in enumerate(nodes):
            node.seq_num = i
            if self.version_volume == VersionVolume.HYPER_LARGE and i % 100 == 0:
                print(f"{i // 100}% complete")
            try:
                first_link, latest_link, latest_node = ipfs.get_links_to_first_and_latest_nodes(self.url)
                node.linked_iparos = self.linking_strategy.get_candidate_nodes(latest_link, latest_node, first_link)
                self.num_links += len(node.linked_iparos)
            except IPARONotFoundException:
                node.linked_iparos = set()
            cid, _ = ipfs.store(node)
            if i == 0:
                first_node = node
            ipns.update(self.url, cid)

        # Columns: ["strategy", "volume", "density", "num_links", "store_ipns_get",
        #           "store_ipns_update", "store_ipfs_retrieve", "store_ipfs_store"]
        row = [str(x) for x in [self.linking_strategy, self.version_volume, self.version_density,
                                self.num_links, ipns.get_count, ipns.update_count,
                                ipfs.retrieve_count, ipfs.store_count]]

        # "a+" means append to the file.
        with open("results_store.csv", "a+") as file:
            file.write("\t".join(row) + "\n")

        if verbose:
            IPAROSimulationWriter.print_counts("Store")
        print("Retrieve")

        # Columns: ["strategy_name", "type", "volume", "density", "ipfs_retrieve_count"]
        with open("results_retrieve.csv", "a+") as file:
            for t in range(k):
                # This operation does not count.
                self.reset()
                # Get summary statistics
                selected_index = random.randint(0, self.version_volume - 1)

                # The intent is to find separate numbers, where the numbers are not known until at runtime.
                ipfs.retrieve_iparo_by_url_and_number(self.url, selected_index)

                row = [str(x) for x in [self.linking_strategy, "number", self.version_volume,
                                        self.version_density, ipfs.retrieve_count]]

                file.write("\t".join(row) + "\n")
                # Get counts for retrieve
                if verbose:
                    IPAROSimulationWriter.print_counts("Retrieve")

                # Choose a random timestamp. This should not get penalized.
                first_link, latest_link, latest_node = ipfs.get_links_to_first_and_latest_nodes(self.url)
                selected_timestamp = random.randint(first_node.timestamp, latest_node.timestamp)
                self.reset()
                ipfs.retrieve_iparo_by_url_and_timestamp(self.url, selected_timestamp)

                row = [str(x) for x in [self.linking_strategy, "date", self.version_volume,
                                        self.version_density, ipfs.retrieve_count]]
                file.write("\t".join(row) + "\n")

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

    # def as_graph(self):
    #     """
    #     Creates a DiGraph object out of the current nodes in the IPFS.
    #     """
    #     # Do comprehensive
    #     nx_graph = nx.DiGraph()
    #     for iparo in ipfs.get_all_iparos(self.url):
    #         curr_num = iparo.seq_num
    #         nx_graph.add_node(curr_num)
    #         for link in iparo.linked_iparos:
    #             nx_graph.add_edge(curr_num, link.seq_num)
    #
    #     return nx_graph

    def reset(self, reset_data=False):
        """Resets the counts (and optionally, the data) from the IPNS and IPFS."""
        if reset_data:
            ipfs.reset_data()
            ipns.reset_data()
            self.num_links = 0
        ipfs.reset_counts()
        ipns.reset_counts()


if __name__ == "__main__":
    linking_strategies = {
        "Single": [SingleStrategy()],
        "Comprehensive": [ComprehensiveStrategy()],
        "K-Previous": [PreviousStrategy(), KPreviousStrategy(2), KPreviousStrategy(4),
                       KPreviousStrategy(8), KPreviousStrategy(16)],
        "Sequential S-Max-Gap": [SequentialSMaxGapStrategy(2),
                                 SequentialSMaxGapStrategy(4),
                                 SequentialSMaxGapStrategy(8),
                                 SequentialSMaxGapStrategy(16),
                                 SequentialSMaxGapStrategy(32)],
        "Sequential Uniform N-Prior": [SequentialUniformNPriorStrategy(1),
                                       SequentialUniformNPriorStrategy(2),
                                       SequentialUniformNPriorStrategy(4),
                                       SequentialUniformNPriorStrategy(8),
                                       SequentialUniformNPriorStrategy(16)],
        "Sequential Exponential": [SequentialExponentialStrategy(1.25),
                                   SequentialExponentialStrategy(1.5),
                                   SequentialExponentialStrategy(2),
                                   SequentialExponentialStrategy(2.5),
                                   SequentialExponentialStrategy(3),
                                   SequentialExponentialStrategy(4)],
        "Temporally Uniform": [TemporallyUniformStrategy(1),
                               TemporallyUniformStrategy(2),
                               TemporallyUniformStrategy(4),
                               TemporallyUniformStrategy(8),
                               TemporallyUniformStrategy(16)],
        "Temporally Min Gap": [TemporallyMinGapStrategy(10),
                               TemporallyMinGapStrategy(20),
                               TemporallyMinGapStrategy(40),
                               TemporallyMinGapStrategy(80),
                               TemporallyMinGapStrategy(160)],
        "Temporally Exponential (Base)": [TemporallyExponentialStrategy(1.25, 10),
                                          TemporallyExponentialStrategy(1.5, 10),
                                          TemporallyExponentialStrategy(2, 10),
                                          TemporallyExponentialStrategy(2.5, 10),
                                          TemporallyExponentialStrategy(3, 10),
                                          TemporallyExponentialStrategy(4, 10)],
        "Temporally Exponential (Time Unit)": [TemporallyExponentialStrategy(2, 1),
                                               TemporallyExponentialStrategy(2, 2),
                                               TemporallyExponentialStrategy(2, 4),
                                               TemporallyExponentialStrategy(2, 8),
                                               TemporallyExponentialStrategy(2, 16),
                                               TemporallyExponentialStrategy(2, 32)],
    }


    version_densities = [
        UniformVersionDensity(1000),
        LinearVersionDensity(2, 1000),
        BigHeadLongTailVersionDensity(5, 1000),
        MultipeakVersionDensity(np.array([0.5, 0.5]), np.array([[0, 50], [200, 100]])),
    ]
    os.chdir("../..")

    # Make a separate folder called "results"
    os.makedirs("results", exist_ok=True)
    os.chdir("results")

    # Write to file.
    with open("results_store.csv", "w+") as file:
        headers = ["strategy", "volume", "density", "num_links", "store_ipns_get",
                   "store_ipns_update", "store_ipfs_retrieve", "store_ipfs_store"]
        file.write("\t".join(headers) + "\n")

    with open("results_retrieve.csv", "w+") as file:
        headers = ["strategy_name", "type", "volume", "density", "ipfs_retrieve_count"]
        file.write("\t".join(headers) + "\n")

    keys = ["get", "update", "retrieve", "store"]
    volumes = [volume for volume in VersionVolume if volume > 1]

    for name, strategies in linking_strategies.items():
        for density in version_densities:
            os.makedirs(os.path.join(name, str(density)), exist_ok=True)

    for name, strategies in linking_strategies.items():
        for strategy in strategies:
            simulation = IPAROSimulationWriter(linking_strategy=strategy,
                                               version_volume=VersionVolume.MEDIUM,
                                               version_density=UniformVersionDensity())
            # 3 types of operations to test (store, retrieve by number, retrieve by date),
            # 4 types of IPFS/IPNS operations to count, 4 version volumes
            store_counts = np.zeros((4, 4))

            # Count number of links
            num_links = np.zeros(4)

            # Count number of retrievals
            for version_density in version_densities:
                retrieve_number_data = []
                retrieve_date_data = []
                simulation.version_density = version_density
                for j, volume in enumerate(volumes):
                    simulation.version_volume = volume
                    simulation.run(100, verbose=False)
                    simulation.reset(reset_data=True)
    # nx.draw_networkx(simulation.as_graph(), arrows=True)
    # plt.show()
