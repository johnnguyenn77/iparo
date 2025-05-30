from test.SysIPAROTestConstant import *
from system.IPFS import IPFS
from system.IPARO import IPARO
from system.IPAROLink import IPAROLink
from system.IPAROLinkFactory import IPAROLinkFactory
from system.IPAROException import IPARONotFoundException
from system.Utils import Utils
from datetime import datetime
import unittest
import pickle
from unittest.mock import patch, MagicMock # mock object library
from enum import Enum

# Import Mode enum from IPFS
from system.IPFS import Mode


class IPFSTest(unittest.TestCase):
    
    def setUp(self):
        self.ipfs = IPFS()
        # Create a set of test IPAROs with linked structure for testing
        self.setup_test_iparos()
    
    def setup_test_iparos(self):
        """
        Sets up a chain of IPAROs for testing with different timestamps and sequence numbers
        """
        # We'll use the test constants, but also create additional ones for specific tests
        self.test_iparos = {}
        self.test_cids = {}
        self.test_links = {}
        
        # Create a mock response for the store method
        self.mock_store_response = {"Hash": "test_cid"}
    
    def test_ipfs_store(self):
        """Test that store correctly serializes and posts to IPFS"""
        # replace requests.post with a mock to intercept actual network calls
        with patch('requests.post') as mock_post:
            # mock the response from the API
            mock_post.return_value.json.return_value = {"Hash": "test_cid_123"}
            
            cid = self.ipfs.store(iparo1)
            
            # Check method was called exactly 1
            mock_post.assert_called_once()
            
            # check the cid is matched with the mock data
            self.assertEqual(cid, "test_cid_123")
    
    def test_ipfs_retrieve(self):
        """Test that retrieve correctly deserializes an IPARO object"""
        with patch('requests.post') as mock_post:
            # Create pickled IPARO data
            pickled_data = pickle.dumps(iparo1)
            mock_post.return_value.status_code = 200
            mock_post.return_value.content = pickled_data
            
            retrieved_iparo = self.ipfs.retrieve("test_cid")
            
            # Verify the retrieved IPARO matches the original
            self.assertEqual(retrieved_iparo.url, iparo1.url)
            self.assertEqual(retrieved_iparo.timestamp, iparo1.timestamp)
    
    def test_ipfs_retrieve_error(self):
        """Test error handling when retrieving fails"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 404
            
            with self.assertRaises(Exception):
                self.ipfs.retrieve("nonexistent_cid")
    
    def test_ipfs_retrieve_by_number_valid(self):
        """Test retrieving an IPARO by valid sequence number"""
        # Setup chain of IPAROs
        iparo3 = MagicMock(spec=IPARO)
        iparo2 = MagicMock(spec=IPARO)
        iparo1 = MagicMock(spec=IPARO)
        
        # Create mock links
        link3 = MagicMock(spec=IPAROLink)
        link3.seq_num = 3
        link3.cid = "cid3"
        
        link2 = MagicMock(spec=IPAROLink)
        link2.seq_num = 2
        link2.cid = "cid2"
        
        link1 = MagicMock(spec=IPAROLink)
        link1.seq_num = 1
        link1.cid = "cid1"
        
        # Setup linked structure
        iparo3.linked_iparos = [link2, link1]
        iparo2.linked_iparos = [link1]
        
        # Mock the retrieve method
        with patch.object(self.ipfs, 'retrieve') as mock_retrieve:
            mock_retrieve.side_effect = lambda cid: {
                "cid3": iparo3,
                "cid2": iparo2,
                "cid1": iparo1
            }[cid]
            
            # Test retrieving specific sequence
            retrieved_link, retrieved_iparo = self.ipfs.retrieve_by_number(link3, 2)
            
            self.assertEqual(retrieved_link, link2)
            self.assertEqual(retrieved_iparo, iparo2)
