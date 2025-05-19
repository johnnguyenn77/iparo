import hashlib
import pickle
import unittest
from unittest import TestCase

from datetime import datetime, timedelta
from system.IPARO import IPARO
from system.IPAROLink import IPAROLink
from system.IPAROLinkFactory import IPAROLinkFactory
from system.IPFS import IPFS, Mode

prev_link = None
latest_link = None
time1 = datetime.fromisoformat("2016-12-31T11:00:00Z")
mock_iparos = {}
ipfs = IPFS()
for i in range(100):
    linked_iparos: frozenset[IPAROLink] = frozenset({prev_link}) if prev_link is not None else frozenset({})
    ts = datetime.fromisoformat("2016-12-31T11:00:00Z") + timedelta(hours=i)
    curr_iparo = IPARO(content_type="application/http; msgtype=response",
                       seq_num=i,
                       timestamp=ts.isoformat().replace("+00:00", "Z"),
                       url="http://memento.us/",
                       content=b"Hello",
                       linked_iparos=linked_iparos)
    # Mock a hash function
    iparo_hash = hashlib.sha256(pickle.dumps(curr_iparo)).hexdigest()
    cid = "Qm" + iparo_hash[:34]  # Not sure why they chose this number.
    # "Store" an IPARO.
    mock_iparos[cid] = curr_iparo
    prev_link = IPAROLinkFactory.from_cid_iparo(cid, curr_iparo)

latest_cid = prev_link.cid


def test_timestamp(rel_time: timedelta, mode: Mode = Mode.CLOSEST):
    time = time1 + rel_time
    time_string = time.isoformat().replace("+00:00", "Z")
    iparo, _ = ipfs.retrieve_by_date(latest_cid, time_string, mode)
    return iparo.seq_num

class IPFSDateTest(TestCase):

    def setUp(self):
        def mock_return(cid: str):
            return mock_iparos[cid]
        ipfs.retrieve = mock_return

    def test_ipfs_should_retrieve_later_time_if_two_closest_timestamps_are_equally_distant(self):
        seq_num = test_timestamp(timedelta(hours=5, minutes=30))
        self.assertTrue(seq_num == 5 or seq_num == 6)

    def test_ipfs_should_retrieve_earlier_time_if_closest_timestamp_is_earlier(self):
        seq_num = test_timestamp(timedelta(hours=5, minutes=29))
        self.assertEqual(seq_num, 5)

    def test_ipfs_should_retrieve_later_time_if_closest_timestamp_is_later(self):
        seq_num = test_timestamp(timedelta(hours=5, minutes=31))
        self.assertEqual(seq_num, 6)
        
    def test_ipfs_should_retrieve_earliest_time_after_timestamp(self):
        seq_num = test_timestamp(timedelta(hours=5, minutes=1), Mode.EARLIEST_AFTER)
        self.assertEqual(seq_num, 6)

    def test_ipfs_should_retrieve_latest_time_before_timestamp(self):
        seq_num = test_timestamp(timedelta(hours=5, minutes=59), Mode.LATEST_BEFORE)
        self.assertEqual(seq_num, 5)

    def test_ipfs_should_retrieve_first_node_if_target_timestamp_comes_before(self):
        seq_num = test_timestamp(timedelta(hours=-5))
        self.assertEqual(seq_num, 0)

    def test_ipfs_should_retrieve_latest_node_if_target_timestamp_comes_after(self):
        seq_num = test_timestamp(timedelta(hours=101))
        self.assertEqual(seq_num, 99)


if __name__ == '__main__':
    unittest.main()
