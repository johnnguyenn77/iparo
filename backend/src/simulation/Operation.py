import os.path
import random
from abc import abstractmethod

import numpy as np
import pandas as pd

from simulation.IPAROException import IPARONotFoundException
from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment
from simulation.IPFS import ipfs
from simulation.IPNS import ipns
from simulation.VersionDensity import VersionGenerator

URL = "example.com"


# Resets the data.
def reset(reset_data=False):
    """Resets the counts (and optionally, the data) from the IPNS and IPFS."""
    if reset_data:
        ipfs.reset_data()
        ipns.reset_data()
    ipfs.reset_counts()
    ipns.reset_counts()


class Operation:
    """
    The Operation class is designed to encapsulate each operation from the user input.
    """

    @abstractmethod
    def execute(self):
        """
        Executes operations based on the environmental parameters.
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        The name of the operation.
        """
        pass


class IterableOperation(Operation):

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True, iterations: int = 0):
        """
        Iterable operation constructor. If number of iterations is not specified (or is 0),
        then the environment iteration number is used. Otherwise, the number of iterations overrides the
        environment number.
        """
        self.env = env
        self.iterations = iterations or env.iterations
        self.opcounts = None
        self.data = np.zeros((self.iterations, 4), dtype=np.float64)
        self.output_path = f"{str(self.env)}-{self.name()}.csv"
        self.save_to_file = save_to_file

    def execute(self):
        """
        Executes the operation.
        """
        needs_setup = True
        try:
            ipns.get_latest_cid(URL)
            needs_setup = False
        except IPARONotFoundException:
            pass  # Ignored
        finally:
            reset()

        if not os.path.exists(self.output_path) or needs_setup:
            if self.env.verbose:
                print(f"{str(self.env.linking_strategy)}-{str(self.env)}: Executing the {self.name()} operation.")
            for i in range(self.iterations):
                self.step(i)
                self.record_iteration(i)
            self.opcounts = pd.DataFrame(self.data, columns=["IPNS Get", "IPNS Update", "IPFS Store",
                                                             "IPFS Retrieve"],
                                         index=pd.RangeIndex(1, self.iterations + 1), dtype=np.uint64)
            self.opcounts.rename_axis(index="Iteration", inplace=True)
            self.postprocess_data()
            if self.save_to_file:
                self.record()
        else:
            print(f"{self.output_path}: Record exists: Skipping")

    @abstractmethod
    def step(self, i: int):
        """
        Each iteration will invoke the step() method.
        """
        pass

    def record_iteration(self, i: int):
        ipfs_counts = ipfs.get_counts()
        ipns_counts = ipns.get_counts()
        # First four elements
        self.data[i, :] = [ipns_counts["get"], ipns_counts["update"],
                           ipfs_counts["store"], ipfs_counts["retrieve"]]
        reset()

    def postprocess_data(self):
        """
        Does post-processing if necessary
        """
        pass

    def record(self):
        """
        Saves the output (and its summary) to a file.
        """
        self.opcounts.rename_axis(index="Iteration", inplace=True)
        storage_summary = self.opcounts.describe()  # Transpose
        path = os.path.join(self.env.output_dir, self.output_path)
        self.opcounts.to_csv(path)
        storage_summary.to_csv(path, mode="a", header=False)


class StoreOperation(IterableOperation):

    def name(self) -> str:
        return "Store"

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file, env.version_volume)
        generator = VersionGenerator(env.version_density)
        self.__num_links = []
        self.__nodes = generator.generate(env.version_volume, URL)

    def step(self, i: int):
        """
        Gets the first operation.
        """
        self.__nodes[i].seq_num = i
        if i % 100 == 99 and self.env.verbose:
            print(f"{str(self.env.linking_strategy)}-{str(self.env)}: Storing node {i + 1}.")
        try:
            first_link, latest_link, latest_node = ipfs.get_links_to_first_and_latest_nodes(URL)
            self.__nodes[i].linked_iparos = self.env.linking_strategy.get_candidate_nodes(latest_link, latest_node,
                                                                                          first_link)
        except IPARONotFoundException:
            self.__nodes[i].linked_iparos = set()

        num_links = len(self.__nodes[i].linked_iparos)
        self.__num_links.append(num_links)

        cid, _ = ipfs.store(self.__nodes[i])
        ipns.update(URL, cid)

    def postprocess_data(self):
        # Append Link counts to opcount data.
        self.opcounts = pd.concat((self.opcounts, pd.Series(self.__num_links, name="Links",
                                                            index=pd.RangeIndex(1, self.iterations + 1))), axis=1)


class FirstOperation(IterableOperation):
    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file)

    def name(self) -> str:
        return "First"

    def step(self, i):
        latest_link, _ = ipfs.get_link_to_latest_node(URL)
        ipfs.retrieve_nth_iparo(0, latest_link)


class LatestOperation(IterableOperation):
    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file)

    def name(self) -> str:
        return "Latest"

    def step(self, i):
        ipfs.get_link_to_latest_node(URL)


class GetNthOperation(IterableOperation):
    """
    Get Nth IPARO
    """

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file)

    def name(self) -> str:
        return "Nth"

    def step(self, i):
        x = random.randint(0, self.env.version_volume - 1)
        latest_link, _ = ipfs.get_link_to_latest_node(URL)
        ipfs.retrieve_nth_iparo(x, latest_link)


class GetAtTOperation(IterableOperation):
    """
    Get at Time T
    """

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file)

    def name(self) -> str:
        return "Time"

    def step(self, i):
        x = random.randint(0, self.env.version_volume - 1)
        latest_link, _ = ipfs.get_link_to_latest_node(URL)
        ipfs.retrieve_nth_iparo(x, latest_link)


class ListAllOperation(IterableOperation):
    """
    List all nodes.
    """

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file)

    def name(self) -> str:
        return "List"

    def step(self, i):
        if self.env.verbose:
            print(f"{str(self.env)}: List All: Iteration {i + 1}")
        ipfs.get_all_links(URL)


class UnsafeListAllOperation(IterableOperation):
    """
    List all nodes for resilience testing.
    """

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file: bool = True):
        super().__init__(env, save_to_file, iterations=env.version_volume)
        self.__links_found = []

    def name(self) -> str:
        return "List-Unsafe"

    def step(self, i):
        if self.env.verbose:
            print(f"{str(self.env)}: Unsafe List All: Iteration {i + 1}")

        missing_nodes = ipfs.remove_nodes(i)
        links_found = ipfs.get_all_links(URL)
        self.__links_found.append(len(links_found) / (self.env.version_volume - i))
        ipfs.restore(missing_nodes)


class IteratedStoreOperation(IterableOperation):

    def name(self) -> str:
        return "Store"

    def __init__(self, env: IPAROSimulationEnvironment, save_to_file=True):
        super().__init__(env, save_to_file)
        self.__num_links = []
        self.df = np.zeros((self.iterations * self.env.version_volume, 4))
        self.__generator = VersionGenerator(self.env.version_density)

    def step(self, i: int):
        """
        Gets the first operation.
        """
        if self.env.verbose:
            print(f"{str(self.env.linking_strategy)}-{str(self.env)}: Iteration {i}.")

        volume = self.env.version_volume
        nodes = self.__generator.generate(volume, URL)
        reset()
        for j in range(volume):
            if j % 100 == 99:
                print(f"{str(self.env.linking_strategy)}-{str(self.env)}: Storing {j + 1}th node.")
            try:
                nodes[j].seq_num = j
                first_link, latest_link, latest_node = ipfs.get_links_to_first_and_latest_nodes(URL)
                nodes[j].linked_iparos = self.env.linking_strategy.get_candidate_nodes(latest_link, latest_node,
                                                                                       first_link)
            except IPARONotFoundException:
                nodes[j].linked_iparos = set()

            num_links = len(nodes[j].linked_iparos)
            self.__num_links.append(float(num_links))

            cid, _ = ipfs.store(nodes[j])
            ipns.update(URL, cid)

            # Record iteration here.
            ipfs_counts = ipfs.get_counts()
            ipns_counts = ipns.get_counts()
            # First four elements
            self.df[volume * i + j, :] = [float(ipns_counts["get"]), float(ipns_counts["update"]),
                                          float(ipfs_counts["store"]), float(ipfs_counts["retrieve"])]
        if i != self.env.iterations - 1:
            reset(reset_data=True)

    def postprocess_data(self):
        volume = self.env.version_volume
        df = pd.DataFrame({"Iteration Number": [1 + i for _ in range(self.env.iterations) for i in range(volume)],
                           "Links": self.__num_links})
        self.opcounts = (pd.concat((pd.DataFrame(self.df, columns=["IPNS Get", "IPNS Update",
                                                                   "IPFS Store", "IPFS Retrieve"]), df), axis=1)
                         .groupby(by=["Iteration Number"]).mean())
        self.opcounts.index = pd.RangeIndex(1, volume + 1)
