import math
from math import ceil, log2
import unittest
from itertools import takewhile, count

from IPAROTestHelpers import *


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
        lengths = test_strategy(KRandomStrategy(10))

        self.assertLessEqual(max(lengths), 12)
        self.assertEqual(min(lengths[1:]), 1)

    def test_exponential_strategy_should_have_logarithmic_number_of_links(self):
        strategy = SequentialExponentialStrategy(k=2)
        lengths = test_strategy(strategy)
        expected_lengths = [0]
        expected_lengths.extend([1 + ceil(log2(i)) for i in range(1, 100)])

        self.assertListEqual(lengths, expected_lengths)

    def test_exponential_strategy_should_have_the_right_nodes(self):
        strategy = SequentialExponentialStrategy(k=2)

        def get_sequence_numbers(n):
            if n == 0:
                return {}
            # Node N maps to N - 1, N - 2, N - 4, and so on, until we hit 0.
            numbers = set(takewhile(lambda x: x > 0, map(lambda x: int(n - math.exp2(x)), count())))
            numbers.update({0, n-1})  # Obviously, we want to add the previous and latest nodes.
            return numbers

        sequence_numbers = []
        expected_sequence_numbers = [sorted(get_sequence_numbers(i)) for i in range(100)]
        for i in range(100):
            content = generate_random_content_string()
            try:
                first_link, latest_link, latest_iparo = ipfs.get_links_to_first_and_latest_nodes(URL)
                linked_iparos = strategy.get_candidate_nodes(latest_link, latest_iparo, first_link)
            except IPARONotFoundException:
                linked_iparos = set()
            timestamp = time1 + i * TimeUnit.SECONDS
            iparo = IPARO(content=content, timestamp=timestamp,
                          url=URL, seq_num=i, linked_iparos=linked_iparos)
            cid, _ = ipfs.store(iparo)
            current_numbers = sorted(link.seq_num for link in linked_iparos)
            sequence_numbers.append(current_numbers)

            ipns.update(URL, cid)

        self.assertListEqual(sequence_numbers, expected_sequence_numbers)

    def test_sequential_uniform_strategy_should_have_at_most_n_plus_two_links(self):
        strategy = SequentialUniformNPriorStrategy(n=10)
        lengths = test_strategy(strategy)
        expected_lengths = [min(i, 12) for i in range(100)]

        self.assertListEqual(lengths, expected_lengths)

    def test_sequential_s_max_gap_strategy_should_respect_s_max_gap(self):
        s = 3 
        strategy = SequentialSMaxGapStrategy(s=s)

        lengths, cids, iparos = test_strategy_verbose(strategy)

        expected_lengths = []
        for i in range(100):
            if i <= 2:
                expected_lengths.append(i)
            else:
                additional_links = max(0, (i - 2) // s)
                expected_lengths.append(2 + additional_links)

        self.assertListEqual(lengths, expected_lengths)

        for i in range(1, 100):
            linked_seq_nums = sorted(link.seq_num for link in iparos[i].linked_iparos)
            self.assertIn(0, linked_seq_nums)
            self.assertIn(i - 1, linked_seq_nums)
            for j in range(1, len(linked_seq_nums)):
                gap = linked_seq_nums[j] - linked_seq_nums[j - 1]
                self.assertLessEqual(gap, s)

    def test_sequential_s_max_gap_strategy_should_be_at_most_s_hops_away(self):
        test_strategy(SequentialSMaxGapStrategy(5))
        # Now use BFS
        latest_cid = ipns.get_latest_cid(URL)
        frontier = [latest_cid]
        bfs_values = {latest_cid: 0}
        while frontier:
            curr_cid = frontier.pop(0)
            curr = ipfs.retrieve(curr_cid)

            for iparo_link in curr.linked_iparos:
                if iparo_link.cid not in bfs_values:
                    bfs_values[iparo_link.cid] = bfs_values[curr_cid] + 1

        # Iterate over BFS values
        self.assertLessEqual(max(bfs_values.values()), 5)

    def test_temporal_uniform_strategy_should_split_into_roughly_equal_time_intervals(self):
        # 0, 10, 11, ..., 44, 50
        relative_times = [(i * 10 + j) for i in range(5) for j in range(i+1)]
        relative_times.append(50)
        timestamps = test_strategy_with_time_distribution(TemporallyUniformStrategy(5), relative_times)
        # 0, 10, 20, 30, 40
        expected_timestamps = [10*i for i in range(6)]

        self.assertListEqual(timestamps, expected_timestamps)

    def test_temporal_max_gap_strategy_should_pick_correct_datetimes(self):
        # 0, 800, 801, ..., 1600
        relative_times = [100 * int(16 - math.exp2(4 - i)) + j for i in range(5) for j in range(i + 1)]
        relative_times.append(1600)
        timestamps = test_strategy_with_time_distribution(
            TemporallyMinGapStrategy(500), relative_times)

        expected_timestamps = [0, 800, 1200, 1600]

        self.assertListEqual(timestamps, expected_timestamps)

    def test_temporal_exponential_strategy_should_get_correct_timestamps(self):
        # 0, 10, 11, ..., 44, 50
        relative_times = [100 * int(16 - math.exp2(4 - i)) + j for i in range(5) for j in range(i + 1)]
        relative_times.append(1600)
        timestamps = test_strategy_with_time_distribution(
            TemporallyExponentialStrategy(2, 100 * TimeUnit.SECONDS), relative_times)
        # 0, 10, 20, 30, 40
        expected_timestamps = [0, 800, 1200, 1400, 1500, 1600]

        self.assertListEqual(timestamps, expected_timestamps)


if __name__ == '__main__':
    unittest.main()
