import unittest

import IPAROSimulationTest
import IPAROStrategyTest
import IPAROTest
import IPFSTest
import IPNSTest
import VersionDensityTest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(IPAROTest))
    suite.addTests(loader.loadTestsFromModule(IPNSTest))
    suite.addTests(loader.loadTestsFromModule(IPFSTest))
    suite.addTests(loader.loadTestsFromModule(IPAROStrategyTest))
    suite.addTests(loader.loadTestsFromModule(VersionDensityTest))
    suite.addTests(loader.loadTestsFromModule(IPAROSimulationTest))

    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
