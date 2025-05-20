import unittest

from test.IPAROTestConstants import *


class IPAROObjectTest(unittest.TestCase):

    def test_has_content(self):
        content = iparo1.content
        self.assertIsInstance(content, bytes)
        self.assertEqual(content, b"123456")

    def test_has_timestamp(self):
        timestamp = iparo1.timestamp
        self.assertIsInstance(timestamp, int)
        self.assertEqual(timestamp, time1)

    def test_has_linked_nodes(self):
        linked_nodes = iparo1.linked_iparos
        self.assertSetEqual(linked_nodes, set())

    def test_has_url(self):
        url = iparo1.url
        self.assertIsInstance(url, str)
        self.assertEqual(url, URL)

    def test_can_be_serialized(self):
        self.assertIsInstance(str(iparo1), str)


class IPAROStorageTest(unittest.TestCase):

    def setUp(self):
        ts = int(1000000 * time.time())
        self.iparo = IPARO(url=URL, content=b"123456", timestamp=ts, linked_iparos=set(), seq_num=0)
        self.iparo2 = IPARO(url=URL2, content=b"1234567", timestamp=ts, linked_iparos=set(), seq_num=1)

    def test_url_is_correct(self):
        self.assertEqual(self.iparo.url, URL)
        self.assertEqual(self.iparo2.url, URL2)

    def test_content_is_correct(self):
        self.assertEqual(self.iparo.content, b"123456")
        self.assertEqual(self.iparo2.content, b"1234567")

    def test_date_is_correct(self):
        self.assertGreaterEqual(int(1000000 * time.time()), self.iparo.timestamp)
        self.assertGreaterEqual(int(1000000 * time.time()), self.iparo2.timestamp)


if __name__ == '__main__':
    unittest.main()
