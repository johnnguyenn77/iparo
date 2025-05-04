import unittest

from IPAROTestConstants import *
from iparo.IPAROException import IPARONotFoundException
from iparo.IPNS import ipns


class IPNSTest(unittest.TestCase):

    def setUp(self):
        ipns.reset_data()
        ipns.reset_counts()

    def test_has_no_urls_initially(self):
        self.assertDictEqual(ipns.get_store(), {})

    def test_returns_none_accessing_invalid_url(self):
        ipns.update(URL, CID1)
        self.assertRaises(IPARONotFoundException, lambda: ipns.get_latest_cid(URL1))

    def test_counts_are_zero_initially(self):
        self.assertEqual(ipns.update_count, 0)
        self.assertEqual(ipns.get_count, 0)

    def test_can_update_url(self):
        ipns.update(URL, CID1)
        self.assertDictEqual(ipns.get_store(), {URL: CID1})
        self.assertEqual(ipns.update_count, 1)

    def test_can_update_url_twice(self):
        ipns.update(URL, CID1)
        ipns.update(URL, CID2)
        self.assertDictEqual(ipns.get_store(), {URL: CID2})
        self.assertEqual(ipns.update_count, 2)

    def test_can_update_two_different_urls(self):
        ipns.update(URL1, CID2)
        ipns.update(URL2, CID1)
        self.assertDictEqual(ipns.get_store(), {URL1: CID2, URL2: CID1})
        self.assertEqual(ipns.update_count, 2)

    def test_can_retrieve_correct_cid(self):
        ipns.update(URL1, CID1)
        ipns.update(URL2, CID2)
        cid = ipns.get_latest_cid(URL1)
        self.assertEqual(cid, CID1)
        self.assertEqual(ipns.get_count, 1)

    def test_can_retrieve_correct_cid_twice(self):
        ipns.update(URL1, CID1)
        ipns.update(URL2, CID2)
        cid1 = ipns.get_latest_cid(URL2)
        cid2 = ipns.get_latest_cid(URL1)
        self.assertEqual(cid1, CID2)
        self.assertEqual(cid2, CID1)
        self.assertEqual(ipns.get_count, 2)


if __name__ == '__main__':
    unittest.main()
