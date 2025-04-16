import unittest

from IPAROTestConstants import *
from IPAROTestHelpers import add_nodes, test_strategy, test_closest_iparo
from iparo.IPAROException import IPARONotFoundException
from iparo.IPAROLinkFactory import IPAROLinkFactory
from iparo.IPFS import ipfs, Mode
from iparo.IPNS import ipns
from iparo.LinkingStrategy import SingleStrategy
from iparo.TimeUnit import TimeUnit

timestamp = int(1000000 * time.time())


class IPFSTest(unittest.TestCase):

    def tearDown(self):
        ipns.reset_data()
        ipns.reset_counts()
        ipfs.reset_data()
        ipfs.reset_counts()

    def test_ipfs_counters_should_be_zero_initially(self):
        self.assertEqual(ipfs.retrieve_count, 0)
        self.assertEqual(ipfs.store_count, 0)

    def test_ipfs_should_initially_have_no_iparos(self):
        self.assertDictEqual(ipfs.data, {})

    def test_ipfs_should_store_one_iparo(self):
        cid = ipfs.store(iparo1)
        self.assertIn(cid, ipfs.data)

    def test_ipfs_should_retrieve_iparos(self):
        cid = ipfs.store(iparo1)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparo1)

    def test_ipfs_should_count_retrievals(self):
        cid = ipfs.store(iparo1)
        ipfs.retrieve(cid)
        self.assertEqual(ipfs.retrieve_count, 1)

    def test_ipfs_should_retrieve_iparos_twice(self):
        cid = ipfs.store(iparo1)
        cid2 = ipfs.store(iparo2)
        node1 = ipfs.retrieve(cid)
        node2 = ipfs.retrieve(cid2)
        self.assertEqual(node1, iparo1)
        self.assertEqual(node2, iparo2)

    # Note: The converse of the proposition implied by the test is not necessarily true.
    # That is, different IPAROs can have the same CIDs, but the same IPARO cannot have
    # two different CIDs. We can see this in more detail when we get there.
    def test_different_cids_should_yield_different_iparos(self):
        cid = ipfs.store(iparo1)
        cid2 = ipfs.store(iparo2)
        node1 = ipfs.retrieve(cid)
        node2 = ipfs.retrieve(cid2)
        self.assertNotEqual(node1, node2)

    def test_ipfs_should_update_retrieval_counts_twice(self):
        cid = ipfs.store(iparo1)
        cid2 = ipfs.store(iparo2)
        ipfs.retrieve(cid)
        ipfs.retrieve(cid2)
        self.assertEqual(ipfs.retrieve_count, 2)

    def test_ipfs_should_store_two_iparos(self):
        cid = ipfs.store(iparo1)
        cid2 = ipfs.store(iparo2)
        self.assertIn(cid, ipfs.data)
        self.assertIn(cid2, ipfs.data)

    def test_ipfs_versions_should_initially_be_empty(self):
        cids = ipfs.get_all_iparos(URL)
        self.assertEqual(len(cids), 0)

    def test_ipfs_versions_should_update_on_one_insert(self):
        cid = ipfs.store(iparo1)
        ipns.update(URL, cid)
        cids = ipfs.get_all_iparos(URL)
        self.assertEqual(len(cids), 1)

    def test_ipfs_versions_should_update_on_two_inserts(self):
        cid = ipfs.store(iparo1)
        ipns.update(URL, cid)

        iparo2.linked_iparos = {IPAROLinkFactory.from_cid_iparo(cid, iparo1)}
        cid2 = ipfs.store(iparo2)
        ipns.update(URL, cid2)
        cids = {link.cid for link in ipfs.get_all_links(URL)}
        self.assertSetEqual(cids, {cid, cid2})

    def test_ipfs_should_retrieve_by_url_and_number(self):
        iparos = add_nodes(3)

        link = ipfs.retrieve_iparo_by_url_and_number(URL, 0)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[0])

    def test_ipfs_should_retrieve_last_node(self):
        iparos = add_nodes(3)

        link = ipfs.retrieve_iparo_by_url_and_number(URL, 2)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[2])

    def test_ipfs_should_retrieve_middle_node(self):
        iparos = add_nodes(10)

        link = ipfs.retrieve_iparo_by_url_and_number(URL, 5)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_latest_time_before_target_timestamp_by_default(self):
        iparos = add_nodes(100)
        timestamp = time1 + 55 * TimeUnit.SECONDS
        link = ipfs.retrieve_by_url_and_timestamp(URL, timestamp)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_raise_error_if_no_iparo_is_inserted_into_ipfs(self):
        self.assertRaises(IPARONotFoundException, lambda: ipfs.retrieve_by_url_and_timestamp(URL, time1, Mode.CLOSEST))
        self.assertRaises(IPARONotFoundException, lambda: ipfs.retrieve_by_url_and_timestamp(URL, time1,
                                                                                             Mode.EARLIEST_AFTER))
        self.assertRaises(IPARONotFoundException, lambda: ipfs.retrieve_by_url_and_timestamp(URL, time1))

    def test_ipfs_should_retrieve_earliest_time_after_target_timestamp(self):
        iparos = add_nodes(100)
        time = time1 + 51 * TimeUnit.SECONDS

        link = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.EARLIEST_AFTER)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[6])

    def test_ipfs_should_retrieve_target_timestamp_if_there_exists_a_cid_with_the_target_timestamp(self):
        iparos = add_nodes(100)

        time = int(time1 + 50 * TimeUnit.SECONDS)

        link1 = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.EARLIEST_AFTER)
        link2 = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.CLOSEST)
        link3 = ipfs.retrieve_by_url_and_timestamp(URL, time)

        links = {link1, link2, link3}
        iparo = ipfs.retrieve(link1.cid)

        self.assertEqual(iparo, iparos[5])
        self.assertSetEqual(links, {link1})

    def test_ipfs_should_retrieve_earlier_time_if_two_closest_timestamps_are_equally_distant(self):
        iparos = add_nodes(100)
        time = int(time1 + 55 * TimeUnit.SECONDS)

        link = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.CLOSEST)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_earlier_time_if_closest_timestamp_is_earlier(self):
        iparos = add_nodes(100)
        time = int(time1 + 54 * TimeUnit.SECONDS)
        link = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.CLOSEST)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_earlier_time_if_closest_timestamp_is_later(self):
        iparos = add_nodes(100)
        time = int(time1 + 56 * TimeUnit.SECONDS)

        link = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.CLOSEST)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[6])

    def test_ipfs_should_retrieve_earliest_time_after_timestamp(self):
        iparos = add_nodes(100)
        time = int(time1 + 54 * TimeUnit.SECONDS)

        link = ipfs.retrieve_by_url_and_timestamp(URL, time, Mode.CLOSEST)
        iparo = ipfs.retrieve(link.cid)
        self.assertEqual(iparo, iparos[5])


class IPAROLinkFactoryTest(unittest.TestCase):

    def setUp(self):
        # Will produce 100 nodes, each uniformly distributed with interval = 1 second.
        test_strategy(SingleStrategy())

    def test_can_throw_when_iparo_seq_num_is_less_than_input_seq_num(self):
        cid = ipns.get_latest_cid(URL)
        iparo = ipfs.retrieve(cid)
        self.assertRaises(IPARONotFoundException, lambda: ipfs.retrieve_nth_iparo(100, iparo))

    def test_can_get_latest_iparo_if_iparo_seq_num_is_equal_to_input_seq_num(self):
        cid = ipns.get_latest_cid(URL)
        iparo = ipfs.retrieve(cid)
        link = IPAROLinkFactory.from_cid_iparo(cid, iparo)
        self.assertEqual(ipfs.retrieve_nth_iparo(99, link), link)

    def test_can_get_nth_iparo_if_iparo_seq_num_is_less_than_input_seq_num(self):
        link = ipfs.retrieve_iparo_by_url_and_number(URL, 55)
        expected_fetched_link = ipfs.retrieve_iparo_by_url_and_number(URL, 44)
        iparo = ipfs.retrieve(link.cid)
        link = IPAROLinkFactory.from_cid_iparo(link.cid, iparo)
        fetched_link = ipfs.retrieve_nth_iparo(44, link)
        self.assertEqual(fetched_link, expected_fetched_link)

    def test_can_get_multiple_indices_in_iparo(self):
        links = [ipfs.retrieve_iparo_by_url_and_number(URL, i*i) for i in range(10)]
        indices = {i * i for i in range(10)}
        cid = ipns.get_latest_cid(URL)
        iparo = ipfs.retrieve(cid)
        link = IPAROLinkFactory.from_cid_iparo(cid, iparo)

        observed = list(IPAROLinkFactory.from_indices(link, indices))

        links.sort(key=lambda link: link.seq_num)
        observed.sort(key=lambda link: link.seq_num)

        self.assertListEqual(observed, links)

    # Test cases:
    # 1. Latest IPARO has exact timestamp.
    def test_can_retrieve_closest_iparo_if_the_closest_iparo_has_exact_timestamp(self):
        observed_iparo_seq_num = test_closest_iparo(0)
        self.assertEqual(observed_iparo_seq_num, 99)

    # 2. Latest IPARO is closest.
    def test_can_retrieve_closest_iparo_if_the_closest_iparo_has_closest_timestamp(self):
        observed_iparo_seq_num = test_closest_iparo(-0.499)
        self.assertEqual(observed_iparo_seq_num, 99)

    # 3. Previous IPARO has exact timestamp.
    def test_can_retrieve_previous_iparo_if_the_previous_iparo_has_exact_timestamp(self):
        observed_iparo_seq_num = test_closest_iparo(-1)
        self.assertEqual(observed_iparo_seq_num, 98)

    # 4. Previous IPARO is closest.
    def test_can_retrieve_previous_iparo_if_the_previous_iparo_has_closest_timestamp(self):
        observed_iparo_seq_num = test_closest_iparo(-0.501)
        self.assertEqual(observed_iparo_seq_num, 98)

    # 5a. Prior nodes are closer.
    def test_can_retrieve_by_timestamp_on_prior_nodes(self):
        observed_iparo_seq_num = test_closest_iparo(-44.1)
        self.assertEqual(observed_iparo_seq_num, 55)

    # 5b. In particular, if first prior node (i.e. node before previous node) is closest, then
    # it should give the first prior node.
    def test_can_retrieve_by_timestamp_on_first_prior_node(self):
        observed_iparo_seq_num = test_closest_iparo(-1.9)
        self.assertEqual(observed_iparo_seq_num, 97)

    # 6. Timestamp comes after latest node.
    def test_can_return_latest_node_if_timestamp_goes_after_latest_timestamp(self):
        observed_iparo_seq_num = test_closest_iparo(1)
        self.assertEqual(observed_iparo_seq_num, 99)

    # 7. Timestamp comes before earliest node.
    def test_can_return_earliest_node_if_timestamp_goes_before_earliest_timestamp(self):
        observed_iparo_seq_num = test_closest_iparo(-120)
        self.assertEqual(observed_iparo_seq_num, 0)


if __name__ == '__main__':
    unittest.main()
