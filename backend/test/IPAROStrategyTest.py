import math
from math import ceil, log2
import unittest

from IPAROTestHelpers import *
from LinkingStrategy import *
from IPAROTestConstants import *


class IPAROStrategyTest(unittest.TestCase):

    def setUp(self):
        ipns.reset_data()
        ipns.reset_counts()
        ipfs.reset_data()
        ipfs.reset_counts()

    def test_single_strategy_should_link_to_only_one_node(self):
        lengths = test_strategy(SingleStrategy())
        expected_lengths = [min(i, 1) for i in range(100)]
        self.assertListEqual(lengths, expected_lengths)

    def test_comprehensive_strategy_should_link_to_all_previous_nodes(self):
        lengths = test_strategy(ComprehensiveStrategy())
        expected_lengths = list(range(100))

        self.assertListEqual(lengths, expected_lengths)

    def test_comprehensive_strategy_should_link_to_the_right_nodes(self):
        lengths, cids, iparos = test_strategy_verbose(ComprehensiveStrategy())
        linked_cids = {link.cid for link in iparos[99].linked_iparos}
        self.assertSetEqual(linked_cids, set(cids[:99]))

    def test_previous_should_link_to_at_most_two_nodes(self):
        lengths, cids, iparos = test_strategy_verbose(PreviousStrategy())

        expected_lengths = [min(i, 2) for i in range(100)]
        self.assertListEqual(lengths, expected_lengths)

    def test_five_previous_should_link_to_at_most_six_nodes(self):
        lengths = test_strategy(KPreviousStrategy(k=5))
        expected_lengths = [min(i, 6) for i in range(100)]

        self.assertListEqual(lengths, expected_lengths)

    def test_random_strategy_should_respect_limits(self):
        lengths = test_strategy(KRandomStrategy(k_min=5, k_max=10))

        self.assertLessEqual(max(lengths), 11)
        self.assertLessEqual(min(lengths[1:]), 1)

    def test_exponential_strategy_should_have_logarithmic_number_of_links(self):
        strategy = SequentialExponentialStrategy(k=2)
        lengths = test_strategy(strategy)
        expected_lengths = [0]
        expected_lengths.extend([1 + ceil(log2(i)) for i in range(1, 100)])

        self.assertListEqual(lengths, expected_lengths)

    def test_exponential_strategy_should_have_the_right_nodes(self):
        strategy = SequentialExponentialStrategy(k=2)

        def get_sequence_numbers(k: int):
            if k == 0:
                return []
            numbers = {0}
            i = 0
            s = k - 1
            while s >= 0:
                numbers.add(int(s))
                i += 1
                s = k - math.exp2(i)

            return sorted(numbers)

        sequence_numbers = []
        expected_sequence_numbers = [get_sequence_numbers(i) for i in range(100)]
        for i in range(100):
            content = generate_random_content_string()
            linked_iparos = strategy.get_linked_nodes(URL)
            iparo = IPARO(content=content, timestamp=(time1 + timedelta(seconds=i)).strftime("%Y%m%d%H%M%S"),
                          url=URL, seq_num=i, linked_iparos=linked_iparos)
            cid = ipfs.store(iparo)
            current_numbers = sorted(link.seq_num for link in linked_iparos)
            sequence_numbers.append(current_numbers)

            ipns.update(URL, cid)

        self.assertListEqual(sequence_numbers, expected_sequence_numbers)

    def test_sequential_uniform_strategy_should_have_at_most_n_plus_two_links(self):
        strategy = SequentialUniformNPriorStrategy(n=10)
        lengths = test_strategy(strategy)
        expected_lengths = [min(i, 12) for i in range(100)]

        self.assertListEqual(lengths, expected_lengths)

    def test_temporal_uniform_strategy_should_split_into_roughly_equal_time_intervals(self):
        # 0, 10, 11, ..., 44, 50
        relative_times = [(i * 10 + j) for i in range(5) for j in range(i+1)]
        relative_times.append(50)
        timestamps = test_strategy_with_time_distribution(TemporallyUniformStrategy(4), relative_times)
        # 0, 10, 20, 30, 40
        expected_timestamps = [10*i for i in range(6)]

        self.assertListEqual(timestamps, expected_timestamps)

    def test_temporal_max_gap_strategy_should_pick_correct_datetimes(self):
        # 0, 800, 801, ..., 1600
        relative_times = [100 * int(16 - math.exp2(4 - i)) + j for i in range(5) for j in range(i + 1)]
        relative_times.append(1600)
        timestamps = test_strategy_with_time_distribution(
            TemporallyMaxGapStrategy(timedelta(seconds=500)), relative_times)

        expected_timestamps = [0, 801, 1600]

        self.assertListEqual(timestamps, expected_timestamps)

    def test_temporal_exponential_strategy_should_get_correct_timestamps(self):
        # 0, 10, 11, ..., 44, 50
        relative_times = [100 * int(16 - math.exp2(4 - i)) + j for i in range(5) for j in range(i + 1)]
        relative_times.append(1600)
        timestamps = test_strategy_with_time_distribution(
            TemporallyExponentialStrategy(2, timedelta(seconds=100)), relative_times)
        # 0, 10, 20, 30, 40
        expected_timestamps = [0, 800, 1200, 1400, 1500, 1600]

        self.assertListEqual(timestamps, expected_timestamps)


if __name__ == '__main__':
    unittest.main()
