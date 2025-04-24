import os

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
        self.num_links = 0
        self.store_results: dict[str, list[int]] = {"get": [], "update": [], "store": [], "retrieve": []}
        self.retrieve_number_results: dict[str, list[int]] = {"get": [], "update": [], "store": [], "retrieve": []}
        self.retrieve_date_results: dict[str, list[int]] = {"get": [], "update": [], "store": [], "retrieve": []}

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

        self.add_counts("store", ipfs.get_counts(), ipns.get_counts())

        if verbose:
            IPAROSimulation.print_counts("Store")
        print("Retrieve")
        for t in range(k):
            self.reset()
            first_link, latest_link, latest_node = ipfs.get_links_to_first_and_latest_nodes(self.url)
            # Get Mean and standard deviation
            selected_index = random.randint(0, latest_node.seq_num - 1)

            # The intent is to find separate numbers, where the numbers are not known until at runtime.
            ipfs.retrieve_iparo_by_url_and_number(self.url, selected_index)

            self.add_counts("retrieve_number", ipfs.get_counts(), ipns.get_counts())
            # Get counts for retrieve
            if verbose:
                IPAROSimulation.print_counts("Retrieve")

            self.reset()
            selected_timestamp = random.randint(first_node.timestamp, latest_node.timestamp)
            ipfs.retrieve_iparo_by_url_and_timestamp(self.url, selected_timestamp)
            self.add_counts("retrieve_date", ipfs.get_counts(), ipns.get_counts())

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

    def reset(self, reset_data=False):
        """Resets the counts (and optionally, the data) from the IPNS and IPFS."""
        if reset_data:
            ipfs.reset_data()
            ipns.reset_data()
            self.num_links = 0
            self.store_results: dict[str, list[int]] = {"get": [], "update": [], "store": [], "retrieve": []}
            self.retrieve_number_results: dict[str, list[int]] = {"get": [], "update": [], "store": [], "retrieve": []}
            self.retrieve_date_results: dict[str, list[int]] = {"get": [], "update": [], "store": [], "retrieve": []}
        ipfs.reset_counts()
        ipns.reset_counts()

    def add_counts(self, phase: str, ipfs_counts: dict[str, int], ipns_counts: dict[str, int]):
        """
        Adds counts to the result dictionary.

        :param phase: The phase that we are adding the results to, either "store", "retrieve_date", or "retrieve_number"
        :param ipfs_counts: The IPFS counts
        :param ipns_counts: The IPNS counts
        """
        if phase == "store":
            results_dict = self.store_results
        elif phase == "retrieve_date":
            results_dict = self.retrieve_date_results
        else:
            results_dict = self.retrieve_number_results
        for key in ipfs_counts.keys():
            results_dict[key].append(ipfs_counts[key])

        for key in ipns_counts.keys():
            results_dict[key].append(ipns_counts[key])


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
        "Temporally Min Gap": [TemporallyMinGapStrategy(1),
                               TemporallyMinGapStrategy(2),
                               TemporallyMinGapStrategy(4),
                               TemporallyMinGapStrategy(8),
                               TemporallyMinGapStrategy(16)],
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
        BigHeadLongTailVersionDensity(5, 1),
        MultipeakVersionDensity(np.array([0.5, 0.5]), np.array([[0, 50], [52, 102]])),
    ]
    os.chdir("../..")

    # Make a separate folder called "results"
    os.makedirs("results", exist_ok=True)
    os.chdir("results")

    keys = ["get", "update", "retrieve", "store"]
    volumes = [volume for volume in VersionVolume if volume > 1]

    for name, strategies in linking_strategies.items():
        for density in version_densities:
            os.makedirs(os.path.join(name, str(density)), exist_ok=True)

    for name, strategies in linking_strategies.items():
        # Do volume
        for strategy in strategies:
            simulation = IPAROSimulation(linking_strategy=strategy,
                                         version_volume=VersionVolume.MEDIUM,
                                         version_density=UniformVersionDensity())
            # 3 types of operations to test (store, retrieve by number, retrieve by date),
            # 4 types of IPFS/IPNS operations to count, 4 version volumes
            store_counts = np.zeros((4, 4))

            # 2 types of IPFS/IPNS operations to count (get, retrieve)
            num_links = np.zeros(4)
            for version_density in version_densities:
                retrieve_number_data = []
                retrieve_date_data = []
                simulation.version_density = version_density
                for j, volume in enumerate(volumes):
                    simulation.version_volume = volume
                    simulation.run(100, verbose=False)
                    for i, key in enumerate(keys):
                        store_counts[i, j] = simulation.store_results[key][0]

                    curr_retrieve_number_results = np.array(simulation.retrieve_number_results["retrieve"],
                                                            dtype=np.float64)
                    curr_retrieve_date_results = np.array(simulation.retrieve_date_results["retrieve"], dtype=np.float64)
                    retrieve_number_data.append(curr_retrieve_number_results)
                    retrieve_date_data.append(curr_retrieve_date_results)
                    num_links[j] = simulation.num_links
                    simulation.reset(reset_data=True)

                # Plot number of different types of operations for each strategy

                # Plot storage
                fig, axes = plt.subplots(2, 2)
                fig.suptitle(f"Storage Performance of {str(strategy)} ({str(version_density)})", wrap=True)

                axes[0, 0].set_title("IPNS Get")
                axes[0, 1].set_title("IPNS Update")
                axes[1, 0].set_title("IPFS Store")
                axes[1, 1].set_title("IPFS Retrieve")

                fig.supxlabel("Version Volume (Number of Nodes)")
                fig.supylabel("Operation Counts")
                for i in range(2):
                    for j in range(2):
                        axes[i, j].plot(volumes, store_counts[2 * i + j, :])
                        axes[i, j].set_xscale("log")
                        axes[i, j].set_yscale("log")
                fig.tight_layout()
                fig.savefig(f"{name}/{str(version_density)}/{str(strategy)} - Store.png")
                plt.close(fig)
                # Plot retrievals

                fig, axes = plt.subplots(2)
                axes[0].boxplot(retrieve_number_data, tick_labels=volumes, showmeans=True)
                axes[1].boxplot(retrieve_date_data, tick_labels=volumes, showmeans=True)
                axes[0].set_yscale("log")
                axes[1].set_yscale("log")
                axes[0].set_ylabel("Retrieve by Number")
                axes[1].set_ylabel("Retrieve by Date")

                fig.suptitle(f"Retrieval Performance of {str(strategy)} ({str(version_density)})", wrap=True)
                fig.supxlabel("Version Volume (Number of Nodes)")
                fig.supylabel("IPFS Retrieval Operation Count")
                fig.tight_layout()
                fig.savefig(f"{name}/{str(version_density)}/{str(strategy)} - Retrieve.png")
                plt.close(fig)

                # Plot link consumption over time
                fig, ax = plt.subplots()
                ax.set_title(f"Version Volume vs. Number of Links - {str(strategy)} ({str(version_density)})", wrap=True)
                ax.set_xscale("log")
                ax.set_xlabel("Version Volume (Number of Nodes)")
                ax.set_yscale("log")
                ax.set_ylabel("Number of Links")
                ax.plot(volumes, num_links)
                fig.tight_layout()
                fig.savefig(f"{name}/{str(version_density)}/{str(strategy)} - Links.png")
                plt.close(fig)

    # nx.draw_networkx(simulation.as_graph(), arrows=True)
    # plt.show()
