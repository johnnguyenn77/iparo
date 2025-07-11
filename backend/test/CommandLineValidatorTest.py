import os
import unittest
from argparse import ArgumentTypeError
from sys import stderr

from simulation.CommandLineValidator import validator, post_validate


def validate(args) -> bool:
    try:
        args = validator.parse_args(args)
        post_validate(args)
    except SystemExit as e:
        return e.code == 0  #
    except ArgumentTypeError:
        return False
    except TypeError:
        return False

    return True


class CommandLineValidatorTest(unittest.TestCase):

    def test_command_line_accepts_single(self):
        is_valid = validate(["--single"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_single_alias(self):
        is_valid = validate(["-s"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_no_parameters_for_single(self):
        is_valid = validate(["--single", 3])
        self.assertFalse(is_valid)

    def test_command_line_accepts_no_parameters_for_single_alias(self):
        is_valid = validate(["-s", 3])
        self.assertFalse(is_valid)

    def test_command_line_does_not_accept_undefined_params(self):
        is_valid = validate(["-x"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_previous(self):
        is_valid = validate(["-p"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_k_previous(self):
        is_valid = validate(["-p", "3"])
        self.assertTrue(is_valid)

    def test_k_previous_requires_no_more_than_one_argument(self):
        is_valid = validate(["-p", "5", "2"])
        self.assertFalse(is_valid)

    def test_k_previous_requires_argument_to_be_int(self):
        is_valid_noninteger = validate(["-p", "3.5"])
        is_valid_alphabetic = validate(["-p", "x"])
        self.assertFalse(is_valid_noninteger or is_valid_alphabetic)

    def test_k_previous_requires_argument_to_be_positive(self):
        is_valid_zero = validate(["-g", "0"])
        is_valid_negative = validate(["-g", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_random_requires_no_more_than_one_argument(self):
        is_valid = validate(["-r", "3", "5"])
        self.assertFalse(is_valid)

    def test_random_requires_that_the_argument_be_positive(self):
        is_valid_zero = validate(["-r", "0"])
        is_valid_negative = validate(["-r", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_random_requires_that_the_argument_be_integer(self):
        is_valid_noninteger = validate(["-r", "3.5"])
        is_valid_alphabetic = validate(["-r", "x"])
        self.assertFalse(is_valid_noninteger or is_valid_alphabetic)

    def test_sequential_uniform_prior_requires_one_argument(self):
        is_valid = validate(["-u"])
        self.assertFalse(is_valid)

    def test_sequential_uniform_prior_requires_no_more_than_one_argument(self):
        is_valid = validate(["-u", "3", "5"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_sequential_uniform_prior(self):
        is_valid = validate(["-u", "3"])
        self.assertTrue(is_valid)

    def test_sequential_uniform_prior_requires_that_the_argument_be_positive(self):
        is_valid_zero = validate(["-u", "0"])
        is_valid_negative = validate(["-u", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_sequential_uniform_prior_requires_that_the_argument_be_an_integer(self):
        is_valid_noninteger = validate(["-u", "3.5"])
        is_valid_alphabetic = validate(["-u", "x"])
        self.assertFalse(is_valid_noninteger or is_valid_alphabetic)

    def test_sequential_max_gap_requires_one_argument(self):
        is_valid = validate(["-g"])
        self.assertFalse(is_valid)

    def test_sequential_max_gap_requires_no_more_than_one_argument(self):
        is_valid = validate(["-g", "5", "2"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_sequential_max_gap(self):
        is_valid = validate(["-g", "3"])
        self.assertTrue(is_valid)

    def test_sequential_max_gap_requires_that_the_argument_be_positive(self):
        is_valid_zero = validate(["-g", "0"])
        is_valid_negative = validate(["-g", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_sequential_max_gap_requires_that_the_argument_be_an_integer(self):
        is_valid_noninteger = validate(["-g", "3.5"])
        is_valid_alphabetic = validate(["-g", "x"])
        self.assertFalse(is_valid_noninteger or is_valid_alphabetic)

    def test_sequential_exponential_requires_one_argument(self):
        is_valid = validate(["-e"])
        self.assertFalse(is_valid)

    def test_sequential_exponential_requires_no_more_than_one_argument(self):
        is_valid = validate(["-e", "5", "2"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_sequential_exponential(self):
        is_valid = validate(["-e", "2.5"])
        self.assertTrue(is_valid)

    def test_sequential_exponential_requires_that_the_argument_be_greater_than_one(self):
        is_valid = validate(["-e", "1"])
        self.assertFalse(is_valid)

    def test_sequential_exponential_requires_that_the_argument_be_positive(self):
        is_valid_negative = validate(["-e", "-0.5"])
        is_valid_zero = validate(["-e", "0"])
        self.assertFalse(is_valid_negative or is_valid_zero)

    def test_temporally_uniform_requires_one_argument(self):
        is_valid = validate(["-U"])
        self.assertFalse(is_valid)

    def test_temporally_uniform_requires_no_more_than_one_argument(self):
        is_valid = validate(["-U", "5", "2"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_temporally_uniform(self):
        is_valid = validate(["-U", "3"])
        self.assertTrue(is_valid)

    def test_temporally_uniform_requires_that_the_argument_be_positive(self):
        is_valid_zero = validate(["-U", "0"])
        is_valid_negative = validate(["-U", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_temporally_uniform_requires_that_the_argument_be_an_integer(self):
        is_valid_noninteger = validate(["-U", "3.5"])
        is_valid_alphabetic = validate(["-U", "2-3"])
        self.assertFalse(is_valid_noninteger or is_valid_alphabetic)

    def test_temporally_min_gap_requires_one_argument(self):
        is_valid = validate(["-G"])
        self.assertFalse(is_valid)

    def test_temporally_min_gap_requires_no_more_than_one_argument(self):
        is_valid = validate(["-G", "5", "2"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_temporally_min_gap(self):
        is_valid = validate(["-G", "3"])
        self.assertTrue(is_valid)

    def test_temporally_min_gap_requires_that_the_argument_be_positive(self):
        is_valid_zero = validate(["-G", "0"])
        is_valid_negative = validate(["-G", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_temporally_min_gap_requires_that_the_argument_be_an_integer(self):
        is_valid_noninteger = validate(["-G", "3.5"])
        is_valid_alphabetic = validate(["-G", "x"])
        self.assertFalse(is_valid_noninteger or is_valid_alphabetic)

    def test_temporally_exponential_requires_two_arguments(self):
        is_valid = validate(["-E", "5"])
        self.assertFalse(is_valid)

    def test_temporally_exponential_requires_no_more_than_two_arguments(self):
        is_valid = validate(["-E", "5", "2", "3"])
        self.assertFalse(is_valid)

    def test_command_line_accepts_temporally_exponential(self):
        is_valid = validate(["-E", "3", "5"])
        self.assertTrue(is_valid)

    def test_temporally_exponential_requires_that_both_arguments_are_numeric(self):
        is_valid_noninteger_first_arg = validate(["-E", "3.5", "y"])
        is_valid_noninteger_second_arg = validate(["-E", "hello", "5.2"])
        self.assertFalse(is_valid_noninteger_first_arg or is_valid_noninteger_second_arg)

    def test_temporally_exponential_requires_that_the_first_argument_be_positive(self):
        is_valid_zero = validate(["-E", "0", "5.3"])
        is_valid_negative = validate(["-E", "-1", "5.7"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_temporally_exponential_requires_that_the_second_argument_be_positive(self):
        is_valid_zero = validate(["-E", "5.3", "0"])
        is_valid_negative = validate(["-E", "5.7", "-1"])
        self.assertFalse(is_valid_zero or is_valid_negative)

    def test_temporally_exponential_requires_that_the_first_argument_be_greater_than_one(self):
        is_valid = validate(["-E", "0.5", "0.5"])
        self.assertFalse(is_valid)

    def test_temporally_exponential_accepts_second_argument_of_less_than_one(self):
        is_valid = validate(["-E", "2", "0.5"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_help(self):
        is_valid = validate(["-h"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_single_volume(self):
        is_valid = validate(["-s", "-V", "single"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_small_volume(self):
        is_valid = validate(["-s", "-V", "small"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_medium_volume(self):
        is_valid = validate(["-s", "-V", "medium"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_large_volume(self):
        is_valid = validate(["-s", "-V", "large"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_hyper_large_volume(self):
        is_valid = validate(["-s", "-V", "hyper_large"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_hyper_large_volume_alias(self):
        is_valid = validate(["-s", "-V", "hyperlarge"])
        self.assertTrue(is_valid)

    def test_command_line_accepts_case_insensitive_volume_alias(self):
        is_valid = validate(["-s", "-V", "HYPERLARGE"])
        self.assertTrue(is_valid)

    def test_command_line_does_not_accept_unrecognized_input(self):
        is_valid = validate(["-s", "-V", "smell"])
        self.assertFalse(is_valid)

    def test_can_parse_linear_density_with_slope_minus_two(self):
        is_valid = validate(["-s", "-l", "-2"])
        self.assertTrue(is_valid)

    def test_can_parse_linear_density_with_slope_two(self):
        is_valid = validate(["-s", "-l", "2"])
        self.assertTrue(is_valid)

    def test_linear_density_cannot_have_non_numeric_arguments(self):
        is_valid = validate(["-s", "-l", "why?"])
        self.assertFalse(is_valid)

    def test_linear_density_cannot_have_arguments_less_than_minus_two(self):
        is_valid = validate(["-s", "-l", "-3"])
        self.assertFalse(is_valid)


    def test_bhlt_density_cannot_have_zero_as_argument(self):
        is_valid = validate(["-s", "-b", "0"])
        self.assertFalse(is_valid)

    def test_bhlt_density_cannot_have_negative_number_as_argument(self):
        is_valid = validate(["-s", "-b", "-1"])
        self.assertFalse(is_valid)

    def test_bhlt_density_cannot_have_one_as_its_argument(self):
        is_valid = validate(["-s", "-b", "1"])
        self.assertFalse(is_valid)

    def test_bhlt_density_could_have_positive_less_than_one_as_argument(self):
        is_valid = validate(["-s", "-b", "0.99"])
        self.assertTrue(is_valid)

    def test_bhlt_density_could_have_positive_greater_than_one_as_argument(self):
        is_valid = validate(["-s", "-b", "0.5"])
        self.assertTrue(is_valid)

    def test_multipeak_density_could_have_positive_greater_than_one_as_argument(self):
        is_valid = validate("-s -m 0.5 0 20 -m 0.5 100 30".split())
        self.assertTrue(is_valid)

    def test_multipeak_density_should_have_positive_weights(self):
        is_valid = validate("-s -m 0.5 0 20 -m -0.5 100 30".split())
        self.assertFalse(is_valid)

    def test_command_line_accepts_get_first_operation(self):
        is_valid = validate("-s -O first".split())
        self.assertTrue(is_valid)

    def test_command_line_accepts_get_latest_operation(self):
        is_valid = validate("-s -O latest".split())
        self.assertTrue(is_valid)

    def test_command_line_accepts_get_time_operation(self):
        is_valid = validate("-s -O time".split())
        self.assertTrue(is_valid)

    def test_command_line_accepts_get_nth_operation(self):
        is_valid = validate("-s -O nth".split())
        self.assertTrue(is_valid)

    def test_command_line_accepts_list_operation(self):
        is_valid = validate("-s -O list".split())
        self.assertTrue(is_valid)

    def test_command_line_accepts_multiple_operations(self):
        is_valid = validate("-s -O list nth".split())
        self.assertTrue(is_valid)

    def test_command_line_does_not_accept_same_operations(self):
        is_valid = validate("-s -O list list".split())
        self.assertFalse(is_valid)

    def test_command_line_does_not_accept_unknown_operation(self):
        is_valid = validate("-s -O what".split())
        self.assertFalse(is_valid)

    def test_command_line_accepts_number_of_iterations(self):
        is_valid = validate("-s -n 200".split())
        self.assertTrue(is_valid)

    def test_command_line_does_not_accept_zero_iterations(self):
        is_valid = validate("-s -n 0".split())
        self.assertFalse(is_valid)

    def test_command_line_does_not_accept_negative_iterations(self):
        is_valid = validate("-s -n -2".split())
        self.assertFalse(is_valid)

    def test_command_line_does_not_accept_non_integer_iterations(self):
        is_valid = validate("-s -n 0.5".split())
        self.assertFalse(is_valid)

    def test_command_line_does_not_accept_non_numeric_iterations(self):
        is_valid = validate("-s -n hotdog".split())
        self.assertFalse(is_valid)

    def test_command_line_accepts_verbosity(self):
        is_valid = validate("-s -n 3 -v".split())
        self.assertTrue(is_valid)

    def test_command_line_accepts_verbosity_without_extra_argument(self):
        is_valid = validate("-s -n 3 -v 5".split())
        self.assertFalse(is_valid)

    def test_command_line_accepts_output(self):
        is_valid = validate("-s -n 3 -o results".split())
        self.assertTrue(is_valid)

    def test_command_line_output_requires_string(self):
        is_valid = validate("-s -n 3 -o".split())
        self.assertFalse(is_valid)

    def test_command_line_output_only_accepts_one_argument_in_directories(self):
        is_valid = validate("-s -n 3 -o results something".split())
        self.assertFalse(is_valid)

    def test_command_line_accepts_results(self):
        try:
            is_valid = validate("-s -n 3 -o results".split())
            self.assertTrue(is_valid)
        finally:
            os.removedirs("results")

    def test_command_line_accepts_interval(self):
        is_valid = validate(["-s", "-i", "0.7"])
        self.assertTrue(is_valid)

    def test_command_line_does_not_accept_negative_numbers(self):
        is_valid = validate(["-s", "-i", "-0.7"])
        self.assertFalse(is_valid)

    def test_command_line_does_not_accept_non_numeric_arguments(self):
        is_valid = validate(["-s", "-i", "apple"])
        self.assertFalse(is_valid)
