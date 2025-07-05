from simulation.LinkingStrategy import *
from simulation.VersionDensity import *


class IPAROSimulationEnvironment:
    """
    The class for the testing environment.
    """

    def __init__(self, linking_strategy: LinkingStrategy, version_volume: VersionVolume,
                 version_density: VersionDensity, operations: list[str], output_dir: str,
                 verbose: bool = False, iterations: int = 100):
        self.linking_strategy = linking_strategy
        self.version_density = version_density
        self.version_volume = version_volume
        self.operations = operations
        self.verbose = verbose
        self.iterations = iterations
        self.output_dir = output_dir or "."

    def __str__(self):
        name = self.version_volume.name
        name = name[0].upper() + name[1:].lower()
        return f"{str(self.linking_strategy)}-{name}-{str(self.version_density)}"
