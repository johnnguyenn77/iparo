import unittest
from simulation.VersionDensity import *


class VersionDensityTestCase(unittest.TestCase):

    def test_version_density_is_uniformly_distributed(self):
        """T3.2.5.1 - Sampling from a Uniform Version Density"""
        uniform_density = UniformVersionDensity()
        generator = VersionGenerator(uniform_density)
        iparos = generator.generate(10000)
        ts = [iparo.timestamp for iparo in iparos]

        self.assertEqual(len(ts), 10000)
        self.assertLessEqual(max(ts) - min(ts), 999999)

    def test_linear_is_linearly_distributed(self):
        """T3.2.5.2 - Sampling from a Linear Version Density"""
        linear_version_density = LinearVersionDensity(2)
        version_generator = VersionGenerator(linear_version_density)
        nodes = version_generator.generate(10000)
        nodes = sorted(nodes, key=lambda node: node.timestamp)

        interval = nodes[-1].timestamp - nodes[0].timestamp

        # Split the interval into 16 equal time intervals
        frequencies = [0] * 16
        for i in range(len(nodes) - 1):
            frac_interval = (nodes[i].timestamp - nodes[0].timestamp) / interval
            idx = min(int(16 * frac_interval ** 2), 15)
            frequencies[idx] += 1

        self.assertLessEqual(np.max(frequencies) - np.min(frequencies), 200)

    def test_big_head_long_tail_has_big_head_and_long_tail(self):
        """T3.2.5.3 - Sampling from a Big Head Long Tail Version Density"""
        big_head_long_tail = BigHeadLongTailVersionDensity(200)
        timestamps = big_head_long_tail.sample(VersionVolume.LARGE)
        timestamps = np.sort(timestamps)
        interval = timestamps[-1] - timestamps[0]
        frac_intervals = [(ts - timestamps[0]) / interval for ts in timestamps]

        # Split the interval into 10 equal time intervals
        frequencies = [0] * 10
        for frequency in frac_intervals:
            idx = min(9, int(frequency * 10))
            frequencies[idx] += 1

        # The first time interval should have at least 20% of the nodes.
        self.assertGreaterEqual(frequencies[0] / VersionVolume.LARGE, 0.2)

    def test_multipeak_can_have_two_peaks(self):
        """T3.2.5.4 - Sampling from a Big Head Long Tail Version Density"""
        multipeak = MultipeakVersionDensity(np.array([2/3, 1/3]),
                                            np.array([[0, 32], [2000, 30]]))
        version_generator = VersionGenerator(multipeak)
        nodes = version_generator.generate(1000)
        nodes = sorted(nodes, key=lambda node: node.timestamp)
        interval = nodes[-1].timestamp - nodes[0].timestamp
        frac_intervals = [(node.timestamp - nodes[0].timestamp) / interval for node in nodes]
        frequencies = [0] * 10
        for frequency in frac_intervals:
            idx = min(9, int(frequency * 10))
            frequencies[idx] += 1

        # The 1st time interval should have more nodes than the 2nd time interval
        self.assertGreater(frequencies[0], frequencies[1])
        # The 10th time interval should have more nodes than the 9th time interval
        self.assertGreater(frequencies[9], frequencies[8])


if __name__ == '__main__':
    unittest.main()
