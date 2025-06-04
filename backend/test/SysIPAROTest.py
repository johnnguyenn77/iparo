import unittest
from datetime import datetime
# backend/test/system/test_iparo.py
from test.SysIPAROTestConstant import *

class IPAROObjectTest(unittest.TestCase):
    
    def test_iparo_constructor_initialization(self):
        """T3.2.1.1 - Creating an IPARO with the constructor"""
        self.assertEqual(iparo1.url, url1)
        self.assertEqual(iparo1.timestamp, time1)
        self.assertEqual(iparo1.content, content1)
        self.assertEqual(iparo1.linked_iparos, frozenset())
        self.assertEqual(iparo1.seq_num, seq_num1)


    def test_iparo_has_content(self):
        content = iparo1.content
        self.assertIsInstance(content, bytes)
        self.assertEqual(content, content1)

    def test_iparo_has_timestamp(self):
        timestamp = iparo1.timestamp
        self.assertIsInstance(timestamp, str)
        self.assertEqual(timestamp, time1)

    def test_iparo_has_linked_nodes(self):
        linked_nodes = iparo1.linked_iparos
        self.assertSetEqual(linked_nodes, set())

    def test_iparo_has_url(self):
        url = iparo1.url
        self.assertIsInstance(url, str)
        self.assertEqual(url, url1)

    def test_iparo_can_be_serialized(self):
        self.assertIsInstance(str(iparo1), str)
        
    def test_iparo_has_more_than_zero_snapshot(self):
        linked_cid = iparo2.linked_iparos
        seq_num = iparo2.seq_num
        for link in linked_cid:
            self.assertIsInstance(link, IPAROLink)
        self.assertEqual(linked_cid, links2)
        self.assertEqual(seq_num, seq_num2)
        
    def test_iparo_linked_nodes_empty(self):
        self.assertEqual(iparo1.linked_iparos, frozenset())
        
    def test_iparo_has_seq_num(self):
        self.assertEqual(iparo1.seq_num, seq_num1)
        self.assertEqual(iparo2.seq_num, seq_num2) 

    def test_iparo_has_content_type(self):
        self.assertEqual(iparo1.content_type, content_type1)

    def test_iparo_has_nonce(self):
        self.assertEqual(iparo1.nonce, 0)
        
    def test_iparo_str_output(self):
        string_output = str(iparo1)
        self.assertIn("http://memento.us", string_output)
        self.assertIsInstance(string_output, str)

if __name__ == '__main__':
    unittest.main()