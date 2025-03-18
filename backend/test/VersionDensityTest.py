import unittest
from iparo.VersionDensity import *


class VersionDensityTestCase(unittest.TestCase):

    def test_uniform_is_uniformly_distributed(self):
        uniform = UniformVersionDensity()
        nodes = uniform.get_iparos(VersionVolume.MEDIUM)
        timedeltas = set()
        # Make sure that the dt's are equal
        for i in range(len(nodes) - 1):
            time_diff = IPARODateConverter.diff(nodes[i+1].timestamp, nodes[i].timestamp)
            timedeltas.add(time_diff)

        self.assertEqual(len(timedeltas), 1)

    def test_linear_is_linearly_distributed(self):
        uniform = LinearVersionDensity(0)
        nodes = uniform.get_iparos(VersionVolume.LARGE)
        interval = IPARODateConverter.diff(nodes[-1].timestamp, nodes[0].timestamp)

        # Split the interval into 16 equal time intervals
        frequencies = [0] * 16
        for i in range(len(nodes) - 1):
            frac_interval = IPARODateConverter.diff(nodes[i].timestamp, nodes[0].timestamp) / interval
            idx = min(int(16 * frac_interval ** 2), 15)
            frequencies[idx] += 1

        self.assertLessEqual(max(frequencies) - min(frequencies), 1)

    def test_big_head_long_tail_has_big_head_and_long_tail(self):
        big_head_long_tail = BigHeadLongTailVersionDensity(20)
        nodes = big_head_long_tail.get_iparos(VersionVolume.LARGE)
        interval = IPARODateConverter.diff(nodes[-1].timestamp, nodes[0].timestamp)
        frac_intervals = [IPARODateConverter.diff(node.timestamp, nodes[0].timestamp) / interval for node in nodes]

        # Split the interval into 10 equal time intervals
        frequencies = [0] * 10
        for frequency in frac_intervals:
            idx = min(9, int(frequency * 10))
            frequencies[idx] += 1

        # The first time interval should have at least 20% of the nodes.
        self.assertGreaterEqual(frequencies[0] / VersionVolume.LARGE, 0.2)
        # The tail should be long (decay factor should be greater than 0.8)
        self.assertGreaterEqual(frequencies[9] / frequencies[8], 0.8)

    def test_multipeak_can_have_two_peaks(self):
        # Reason why I omitted the seed: It turns out that the algorithm used
        # to create normal variates has an "upper bound" according to the random
        # number generator used.

        multipeak = MultipeakDensity([(1, 0, 32), (0.5, 2000, 30)])
        nodes = multipeak.get_iparos(VersionVolume.LARGE)
        interval = IPARODateConverter.diff(nodes[-1].timestamp, nodes[0].timestamp)
        frac_intervals = [IPARODateConverter.diff(node.timestamp, nodes[0].timestamp) / interval for node in nodes]
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
