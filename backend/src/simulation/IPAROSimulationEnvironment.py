from simulation.LinkingStrategy import *
from simulation.VersionDensity import *


class IPAROSimulationEnvironment:
    """
    The class for the testing environment.
    """

    def __init__(self, linking_strategy: LinkingStrategy, version_volume: int,
                 version_density: VersionDensity, operations: list[str], output_dir: str | None = None,
                 verbose: bool = False, iterations: int = 10):
        self.linking_strategy = linking_strategy
        self.version_density = version_density
        self.version_volume = version_volume
        self.operations = operations
        self.verbose = verbose
        self.iterations = iterations
        self.output_dir = output_dir or "."

    def __str__(self):
        return f"{self.version_volume}-{str(self.version_density)}"
