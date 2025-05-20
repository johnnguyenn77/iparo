import unittest
# backend/test/system/test_iparo.py
from test.SysIPAROTestConstants import *

class IPAROObjectTest(unittest.TestCase):

    def test_has_content(self):
        content = iparo1.content
        self.assertIsInstance(content, bytes)
        self.assertEqual(content, content1)

    def test_has_timestamp(self):
        timestamp = iparo1.timestamp
        self.assertIsInstance(timestamp, str)
        self.assertEqual(timestamp, time1)

    def test_has_linked_nodes(self):
        linked_nodes = iparo1.linked_iparos
        self.assertSetEqual(linked_nodes, set())

    def test_has_url(self):
        url = iparo1.url
        self.assertIsInstance(url, str)
        self.assertEqual(url, url1)

    def test_can_be_serialized(self):
        self.assertIsInstance(str(iparo1), str)


if __name__ == '__main__':
    unittest.main()