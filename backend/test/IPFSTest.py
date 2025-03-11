import unittest

from IPAROTestConstants import *
from IPAROTestHelpers import add_nodes
from iparo.IPFS import ipfs, Mode
from iparo.IPNS import ipns

timestamp = datetime.now()


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
        cids = ipfs.get_all_cids(URL)
        self.assertEqual(len(cids), 0)

    def test_ipfs_versions_should_update_on_one_insert(self):
        cid = ipfs.store(iparo1)
        ipns.update(URL, cid)
        cids = ipfs.get_all_cids(URL)
        self.assertEqual(len(cids), 1)

    def test_ipfs_versions_should_update_on_two_inserts(self):
        cid = ipfs.store(iparo1)
        ipns.update(URL, cid)

        iparo2.linked_iparos = {IPAROLinkFactory.from_cid_iparo(cid, iparo1)}
        cid2 = ipfs.store(iparo2)
        ipns.update(URL, cid2)
        cids = ipfs.get_all_cids(URL)
        self.assertSetEqual(set(cids), {cid, cid2})

    def test_ipfs_should_retrieve_by_number(self):
        iparos = add_nodes(3)

        cid = ipfs.retrieve_by_number(URL, 0)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[0])

    def test_ipfs_should_retrieve_last_node(self):
        iparos = add_nodes(3)

        cid = ipfs.retrieve_by_number(URL, 2)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[2])

    def test_ipfs_should_retrieve_middle_node(self):
        iparos = add_nodes(10)

        cid = ipfs.retrieve_by_number(URL, 5)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_latest_time_before_target_timestamp_by_default(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=55))
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_no_iparo_if_no_iparo_is_inserted_into_ipfs(self):
        cids = {ipfs.retrieve_by_timestamp(URL, time1, Mode.CLOSEST),
                ipfs.retrieve_by_timestamp(URL, time1, Mode.EARLIEST_AFTER),
                ipfs.retrieve_by_timestamp(URL, time1)}

        self.assertSetEqual(cids, {None})

    def test_ipfs_should_retrieve_earliest_time_after_target_timestamp(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=51), Mode.EARLIEST_AFTER)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[6])

    def test_ipfs_should_retrieve_target_timestamp_if_there_exists_a_cid_with_the_target_timestamp(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=50), Mode.EARLIEST_AFTER)
        cid2 = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=50), Mode.CLOSEST)
        cid3 = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=50))

        cids = {cid, cid2, cid3}
        iparo = ipfs.retrieve(cid)

        self.assertEqual(iparo, iparos[5])
        self.assertSetEqual(cids, {cid})

    def test_ipfs_should_retrieve_earlier_time_if_two_closest_timestamps_are_equally_distant(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=55), Mode.CLOSEST)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_earlier_time_if_closest_timestamp_is_earlier(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=54), Mode.CLOSEST)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[5])

    def test_ipfs_should_retrieve_earlier_time_if_closest_timestamp_is_later(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=56), Mode.CLOSEST)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[6])

    def test_ipfs_should_retrieve_earliest_time_after_timestamp(self):
        iparos = add_nodes(100)

        cid = ipfs.retrieve_by_timestamp(URL, time1 + timedelta(seconds=54), Mode.CLOSEST)
        iparo = ipfs.retrieve(cid)
        self.assertEqual(iparo, iparos[5])


if __name__ == '__main__':
    unittest.main()
