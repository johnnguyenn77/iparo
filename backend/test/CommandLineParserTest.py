import unittest
from typing import Callable, Any

from simulation.CommandLineParser import CommandLineParser
from simulation.CommandLineValidator import validator
from simulation.LinkingStrategy import *
from simulation.VersionDensity import *


# Helper methods
def get_relevant_output(user_args: list[str], *, action: Callable[[CommandLineParser], Any]):
    """
    Gets the output of a command in the form of a namespace.
    """
    # The data are assumed to be all valid.
    args = validator.parse_args(user_args)

    parser = CommandLineParser(args)
    relevant_output = action(parser)

    return relevant_output


# Helper functions
def get_policy(parser):
    return parser.parse_policy()


def get_volume(parser):
    return parser.parse_volume()


def get_density(parser):
    return parser.parse_density()


def get_operation(parser):
    return parser.parse_operations()


def get_iterations(parser):
    return parser.parse_iterations()


def get_verbosity(parser):
    return parser.parse_verbosity()


class CommandLineParserTest(unittest.TestCase):

    def test_can_parse_single(self):
        strategy = get_relevant_output(["-s"], action=get_policy)
        self.assertIsInstance(strategy, SingleStrategy)

    def test_can_parse_previous(self):
        strategy = get_relevant_output(["-p"], action=get_policy)
        self.assertIsInstance(strategy, PreviousStrategy)

    def test_can_parse_k_previous(self):
        strategy = get_relevant_output(["-p", "3"], action=get_policy)
        self.assertIsInstance(strategy, KPreviousStrategy)
        self.assertEqual(strategy.k, 3)

    def test_can_parse_comprehensive(self):
        strategy = get_relevant_output(["-c"], action=get_policy)
        self.assertIsInstance(strategy, ComprehensiveStrategy)

    def test_can_parse_random(self):
        strategy = get_relevant_output(["-r", "5"], action=get_policy)
        self.assertIsInstance(strategy, KRandomStrategy)

    def test_can_parse_seq_uniform_n_prior(self):
        strategy = get_relevant_output(["-u", "5"], action=get_policy)
        self.assertIsInstance(strategy, SequentialUniformNPriorStrategy)
        self.assertEqual(strategy.n, 5)

    def test_can_parse_seq_max_gap(self):
        strategy = get_relevant_output(["-g", "5"], action=get_policy)
        self.assertIsInstance(strategy, SequentialSMaxGapStrategy)
        self.assertEqual(strategy.s, 5)

    def test_can_parse_seq_exponential(self):
        strategy = get_relevant_output(["-e", "5"], action=get_policy)
        self.assertIsInstance(strategy, SequentialExponentialStrategy)
        self.assertEqual(strategy.k, 5)

    def test_can_parse_temp_uniform(self):
        strategy = get_relevant_output(["-U", "5"], action=get_policy)
        self.assertIsInstance(strategy, TemporalUniformStrategy)
        self.assertEqual(strategy.n, 5)

    def test_can_parse_temp_max_gap(self):
        strategy = get_relevant_output(["-G", "5"], action=get_policy)
        self.assertIsInstance(strategy, TemporalMinGapStrategy)
        self.assertEqual(strategy.min_gap, 5)

    def test_can_parse_temp_exponential(self):
        strategy = get_relevant_output(["-E", "2.2", "5.3"], action=get_policy)
        self.assertIsInstance(strategy, TemporalExponentialStrategy)
        self.assertEqual(strategy.base, 2.2)
        self.assertEqual(strategy.time_unit, 5.3)

    def test_volume_defaults_to_medium(self):
        volume = get_relevant_output(["-s"], action=get_volume)
        self.assertEqual(volume, VersionVolume.MEDIUM)

    def test_can_parse_numeric_volumes(self):
        volume = get_relevant_output(["-s", "-V", "100"], action=get_volume)
        self.assertEqual(volume, 100)

    def test_can_parse_linear_version_density(self):
        density = get_relevant_output(["-s", "-l", "2"], action=get_density)
        self.assertIsInstance(density, LinearVersionDensity)

    def test_can_parse_bhlt_version_density(self):
        density = get_relevant_output(["-s", "-b", "2"], action=get_density)
        self.assertIsInstance(density, BigHeadLongTailVersionDensity)

    def test_can_parse_multipeak_version_density(self):
        density = get_relevant_output(["-s", "-m", "2", "3", "4"], action=get_density)
        self.assertIsInstance(density, MultipeakVersionDensity)
        self.assertListEqual(density.weights.tolist(), [2])
        self.assertListEqual(density.distributions.tolist(), [[3, 4]])

    def test_can_parse_multipeak_version_density_twice(self):
        density = get_relevant_output("-s -m 2 3 4 -m 5 6 7".split(), action=get_density)
        self.assertIsInstance(density, MultipeakVersionDensity)
        self.assertTrue(np.equal(density.weights, np.array([2, 5])).all())
        self.assertTrue(np.equal(density.distributions, np.array([[3, 4], [6, 7]])).all())

    def test_can_parse_uniform_density_as_default(self):
        density = get_relevant_output(["-s"], action=get_density)
        self.assertIsInstance(density, UniformVersionDensity)

    def test_can_parse_every_operation_as_default(self):
        operations = get_relevant_output(["-s"], action=get_operation)

        # Misleading naming by unittest (should be something like "assertEqualsUnordered")
        self.assertCountEqual(operations, ["first", "latest", "nth", "time", "list", "unsafe-list"])

    def test_can_parse_one_operation(self):
        operations = get_relevant_output(["-s", "-O", "latest"], action=get_operation)

        # Misleading naming by unittest (should be something like "assertEqualsUnordered")
        self.assertCountEqual(operations, ["latest"])

    def test_can_parse_multiple_operations(self):
        operations = get_relevant_output(["-s", "-O", "time", "nth"], action=get_operation)

        # Misleading naming by unittest (should be something like "assertEqualsUnordered")
        self.assertCountEqual(operations, ["time", "nth"])

    def test_can_parse_verbosity(self):
        verbose = get_relevant_output(["-s", "-v"], action=get_verbosity)

        self.assertTrue(verbose)

    def test_iterations_should_be_10_by_default(self):
        iterations = get_relevant_output(["-s"], action=get_iterations)

        self.assertEqual(iterations, 10)

    def test_iterations_can_be_set(self):
        iterations = get_relevant_output(["-s", "-n", "10"], action=get_iterations)

        self.assertEqual(iterations, 10)
