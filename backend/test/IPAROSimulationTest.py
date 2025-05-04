import unittest
from unittest.mock import patch, call

from iparo.IPAROException import IPARONotFoundException
from iparo.IPAROSimulation import IPAROSimulation
from iparo.LinkingStrategy import *
from iparo.IPNS import ipns
from iparo.IPFS import ipfs
from iparo.VersionDensity import *


class IPAROSimulationTest(unittest.TestCase):

    def setUp(self):
        linking_strategy = TemporallyUniformStrategy(2)
        self.simulation = IPAROSimulation(linking_strategy=linking_strategy,
                                          version_volume=VersionVolume.MEDIUM,
                                          version_density=UniformVersionDensity())
        self.simulation.run(100, verbose=False)

    def tearDown(self):
        self.simulation.reset(reset_data=True)

    def test_simulation_has_ipns_store_results(self):
        self.assertIsInstance(self.simulation.store_results, dict)

    def test_simulation_has_ipfs_retrieve_number_results(self):
        self.assertIsInstance(self.simulation.retrieve_number_results, dict)

    def test_simulation_has_ipns_retrieve_datetime_results(self):
        self.assertIsInstance(self.simulation.retrieve_date_results, dict)


    def test_simulation_can_reset(self):
        self.simulation.reset()
        self.assertListEqual([ipns.get_count, ipns.update_count,
                              ipfs.store_count, ipfs.retrieve_count], [0] * 4)

    def test_simulation_can_reset_data(self):
        self.simulation.reset(reset_data=True)
        self.assertListEqual([ipns.get_count, ipns.update_count,
                              ipfs.store_count, ipfs.retrieve_count], [0] * 4)

    def test_simulation_can_reset_data_with_no_trace_of_input(self):
        url = self.simulation.url
        self.simulation.reset(reset_data=True)
        self.assertRaises(IPARONotFoundException, lambda: ipns.get_latest_cid(url))
        self.assertEqual(len(ipfs.get_all_links(url)), 0)

    def test_simulation_can_be_exported_as_graph(self):
        graph = self.simulation.as_graph()
        self.assertEqual(graph.number_of_nodes(), VersionVolume.MEDIUM)

    def test_simulation_is_verbose_by_default(self):
        self.simulation.reset()

        # Use mock calls to detect print statements.
        with patch("builtins.print") as mock:
            self.simulation.run(100)
            self.assertIn(call("Store"), mock.mock_calls)
            self.assertIn(call("Retrieve"), mock.mock_calls)
