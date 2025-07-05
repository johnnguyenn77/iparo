import unittest

from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment
from simulation.LinkingStrategy import TemporallyUniformStrategy
from simulation.VersionDensity import VersionVolume, UniformVersionDensity


class IPAROSimulationEnvironmentTest(unittest.TestCase):

    def test_can_render_name_correctly(self):
        linking_strategy = TemporallyUniformStrategy(2)
        env = IPAROSimulationEnvironment(linking_strategy,
                                         VersionVolume.MEDIUM,
                                         UniformVersionDensity())
        self.assertEqual(str(env), "Temporally Uniform (2 Nodes)-Medium-Uniform")

if __name__ == '__main__':
    unittest.main()
