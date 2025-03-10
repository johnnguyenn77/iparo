import unittest

from IPARODateConverter import IPARODateConverter
from IPAROFactory import IPAROFactory
from IPAROTestConstants import *


class IPAROObjectTest(unittest.TestCase):

    def test_has_content(self):
        content = iparo1.content
        self.assertIsInstance(content, bytes)
        self.assertEqual(content, b"123456")

    def test_has_timestamp(self):
        timestamp = iparo1.timestamp
        self.assertIsInstance(timestamp, str)
        self.assertEqual(timestamp, IPARODateConverter.datetime_to_str(time1))

    def test_has_linked_nodes(self):
        linked_nodes = iparo1.linked_iparos
        self.assertSetEqual(linked_nodes, set())

    def test_has_url(self):
        url = iparo1.url
        self.assertIsInstance(url, str)
        self.assertEqual(url, URL)

    def test_can_be_serialized(self):
        self.assertIsInstance(str(iparo1), str)


class IPAROFactoryTest(unittest.TestCase):

    def setUp(self):
        self.iparo = IPAROFactory.create_node(URL, b"123456")
        self.iparo2 = IPAROFactory.create_node(URL2, b"1234567")

    def test_url_is_correct(self):
        self.assertEqual(self.iparo.url, URL)
        self.assertEqual(self.iparo2.url, URL2)

    def test_content_is_correct(self):
        self.assertEqual(self.iparo.content, b"123456")
        self.assertEqual(self.iparo2.content, b"1234567")

    def test_date_is_correct(self):
        self.assertGreaterEqual(datetime.now(), datetime.strptime(self.iparo.timestamp, IPARODateConverter.DATE_FORMAT))
        self.assertGreaterEqual(datetime.now(), datetime.strptime(self.iparo2.timestamp, IPARODateConverter.DATE_FORMAT))


if __name__ == '__main__':
    unittest.main()
