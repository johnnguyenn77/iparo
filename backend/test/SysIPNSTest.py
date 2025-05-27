import unittest
from unittest.mock import patch, Mock
from test.SysIPAROTestConstant import *
import hashlib

from system.IPNS import IPNS

class IPNSTest(unittest.TestCase):

    def setUp(self):
        self.ipns = IPNS()
        self.test_url = "http://example.com"
        self.key_name = f"urlkey-{hashlib.sha256(self.test_url.encode()).hexdigest()[:10]}"
        self.cid = "QmTestCID"
        self.peer_id = "QmTestPeerID"

    @patch("system.IPNS.requests.post")
    def test_ipns_generate_key_for_url_existing_key(self, mock_post):
        # Simulate existing keys
        mock_post.return_value.json.return_value = {
            "Keys": [{"Name": self.key_name}]
        }

        result = self.ipns.generate_key_for_url(self.test_url)
        self.assertEqual(result, self.key_name)

    @patch("system.IPNS.requests.post")
    def test_ipns_generate_key_for_url_new_key(self, mock_post):
        # First call simulates key not found
        mock_post.side_effect = [
            Mock(status_code=200, json=Mock(return_value={"Keys": [{"Name": "otherkey"}]})),
            Mock(status_code=200, json=Mock(return_value={"Name": self.key_name}))
        ]

        result = self.ipns.generate_key_for_url(self.test_url)
        self.assertEqual(result, self.key_name)

    @patch("system.IPNS.requests.post")
    def test_ipns_get_name_for_key_found(self, mock_post):
        mock_post.return_value.json.return_value = {
            "Keys": [{"Name": self.key_name, "Id": self.peer_id}]
        }

        result = self.ipns.get_name_for_key(self.key_name)
        self.assertEqual(result, self.peer_id)

    @patch("system.IPNS.requests.post")
    def test_ipns_get_name_for_key_not_found(self, mock_post):
        mock_post.return_value.json.return_value = {
            "Keys": [{"Name": "someotherkey", "Id": "anotherID"}]
        }

        with self.assertRaises(Exception) as context:
            self.ipns.get_name_for_key(self.key_name)
        self.assertIn("Key", str(context.exception))

    @patch("system.IPNS.requests.post")
    def test_ipns_update_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"Name": self.peer_id}

        result = self.ipns.update(self.key_name, self.cid)
        self.assertEqual(result, self.peer_id)

    @patch("system.IPNS.requests.post")
    def test_ipns_update_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        with self.assertRaises(Exception) as context:
            self.ipns.update(self.key_name, self.cid)
        self.assertIn("Failed to publish", str(context.exception))

    @patch("system.IPNS.requests.post")
    def test_ipns_resolve_cid_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"Path": f"/ipfs/{self.cid}"}

        result = self.ipns.resolve_cid(self.peer_id)
        self.assertEqual(result, self.cid)

    @patch("system.IPNS.requests.post")
    def test_ipns_resolve_cid_failure(self, mock_post):
        mock_post.return_value.status_code = 404
        mock_post.return_value.text = "Not Found"

        with self.assertRaises(Exception) as context:
            self.ipns.resolve_cid(self.peer_id)
        self.assertIn("Failed to resolve", str(context.exception))


if __name__ == "__main__":
    unittest.main()