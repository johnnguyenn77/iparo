import unittest

import IPAROStrategyTest
import IPAROTest
import IPFSTest
import IPNSTest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(IPAROTest))
    suite.addTests(loader.loadTestsFromModule(IPNSTest))
    suite.addTests(loader.loadTestsFromModule(IPFSTest))
    suite.addTests(loader.loadTestsFromModule(IPAROStrategyTest))

    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
