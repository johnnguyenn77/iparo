import unittest
from src.app import app

class APITest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_api_index(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome to the IPARO Web Server", res.data)

    def test_api_ecent_snapshot_missing_url(self):
        res = self.client.get('/api/recent_snapshot')
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Missing 'url'", res.data)

    def test_api_snapshot_count_missing_url(self):
        res = self.client.get('/api/snapshots/count')
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Missing 'url'", res.data)

    def test_api_all_snapshots_missing_url(self):
        res = self.client.get('/api/snapshots')
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Missing 'url'", res.data)

    def test_api_snapshot_by_date_missing_params(self):
        res = self.client.get('/api/snapshots/date')
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Missing 'url' or 'date'", res.data)

if __name__ == '__main__':
    unittest.main()