import os
from sys import stderr
from argparse import ArgumentParser, ArgumentTypeError

from simulation.VersionDensity import VersionVolume

operation_choices = ["first", "latest", "time", "nth", "list"]


# Utility methods used to check validity of command-line args.
def check_positive_int(val):
    """
    A method that will return the parsed positive integer, or raise ArgumentTypeError
    if the input is invalid.
    """
    try:
        ival = int(val)
        if ival <= 0:
            raise ArgumentTypeError(f"{val} is an invalid positive int value")
    except ValueError:
        raise ArgumentTypeError(f"{val} is an invalid positive int value")

    return ival


def check_float(val):
    """
    A method that will return the parsed float,
    or raise ArgumentTypeError if the input is invalid.
    """
    try:
        fval = float(val)
    except ValueError:
        raise ArgumentTypeError(f"{val}")

    return fval


def check_predicate(val, pred):
    """
    Checks whether a floating-point value satisfies a given predicate.
    """
    fval = check_float(val)
    if not pred(fval):
        raise ArgumentTypeError(str(val))
    return fval


# Helper predicates


def check_version_volume(x: str) -> int:
    if x.isdecimal():
        return int(x)
    elif x.lower() in ['single', 'small', 'medium', 'large', 'huge']:
        return VersionVolume[x.upper()]
    raise ArgumentTypeError(str(x))


def check_greater_than_zero(x):
    return check_predicate(x, lambda x: x > 0)


def check_greater_than_one(x):
    return check_predicate(x, lambda x: x > 1)


def check_valid_linear_slope(x):
    return check_predicate(x, lambda x: -2 <= x <= 2)


def check_valid_bhlt_slope(x):
    return check_predicate(x, lambda x: x > 0 and x != 1)


def dir_path(s: str):
    try:
        if not s.endswith(os.sep):
            s += os.sep
        os.makedirs(s, exist_ok=True)
        return s
    except OSError:
        raise ArgumentTypeError(f"Not a valid target directory: {s}")


validator = ArgumentParser(prog="python SimulationWriter.py",
                           description="Generates data about the IPFS/IPNS operation counts for storing and "
                                       "retrieving based on different policies. The default version density "
                                       "to use is uniform.")

validator.add_argument("-o", "--output", help="""The output directory after running the simulation.
Directory names with spaces are unsupported.""",
                       type=dir_path)

# Policy group
policy_group = validator.add_argument_group("Policy", "The policy to use for the simulation.")
policy_exclusive_group = policy_group.add_mutually_exclusive_group(required=True)

# Strategies
policy_exclusive_group.add_argument("-s", "--single", help="Single policy (links to previous node "
                                                           "only).", action="store_true")
policy_exclusive_group.add_argument("-p", "--previous", help="K-Previous policy (links to the "
                                                             "previous and the first node by default), but "
                                                             "can be adjusted to K previous nodes, in addition "
                                                             "to the previous node.", nargs='?', const=1,
                                    type=check_positive_int, metavar="K")
policy_exclusive_group.add_argument("-c", "--comprehensive", help="Comprehensive policy (links to "
                                                                  "all prior nodes).", action="store_true")
policy_exclusive_group.add_argument("-r", "--random", help="K-Random + first + previous policy, "
                                                           "but can be adjusted to K nodes.",
                                    type=check_positive_int, metavar="K")
policy_exclusive_group.add_argument("-u", "--sequniform", help="Sequential N-Uniform Prior. Links to N prior "
                                                               "versions (distributed uniformly across the "
                                                               "sequence of versions), the immediate previous "
                                                               "version, and the first version.",
                                    type=check_positive_int, metavar="N")
policy_exclusive_group.add_argument("-g", "--seqmaxgap", help="Sequential S-Max-Gap, which guarantees "
                                                              "that the necessary number of links to nodes "
                                                              "between the immediate previous and the first "
                                                              "versions that are no more than S hops away. It "
                                                              "ensures that the access time is less than a "
                                                              "given time.", type=check_positive_int,
                                    metavar="S")
policy_exclusive_group.add_argument("-e", "--seqexp", help="Sequential Exponential, which links in such a way "
                                                           "that the version gap is a power of B (base), "
                                                           "starting with the previous node (for instance, "
                                                           "if B = 2, can link 1 version prior, 2 versions "
                                                           "prior, 4, 8, 16, all the way to the first "
                                                           "version). Also links with the first version. If B is not "
                                                           "an integer, then this strategy rounds down to the nearest "
                                                           "integer, but does not round any intermediate "
                                                           "calculations. So if the base is 2.5 (for instance), "
                                                           "the nodes that are 1, 2, 6, and 15 versions prior "
                                                           "would be linked, as well as subsequent nodes.",
                                    type=check_greater_than_one, metavar="base")
policy_exclusive_group.add_argument("-U", "--tempuniform", help="""Temporally N-Uniform Prior. Links to N prior 
                                                                versions (distributed uniformly across the 
                                                                window of time), the immediate previous 
                                                                version, and the first version.""", metavar="N",
                                    type=check_positive_int)
policy_exclusive_group.add_argument("-G", "--tempmingap", help="""Temporally T-min-gap.  Links in such a way 
                                                               that the maximum gap is a window of time T 
                                                               between captures (if present), starting with 
                                                               the immediate previous version. Also links 
                                                               with the first version. T is measured in 
                                                               seconds.""", metavar="T",
                                    type=check_positive_int)
policy_exclusive_group.add_argument("-E", "--tempexp", help="Temporally exponential (with base "
                                                            "and time unit T). Links in such a way "
                                                            "that the maximum gap is a window of time T "
                                                            "between captures (if present), starting with "
                                                            "the immediate previous version. Also links "
                                                            "with the first version. T is measured in seconds, "
                                                            "and base is any number greater than one.",
                                    nargs=2, type=check_greater_than_zero, metavar=("base", "unit"))

# Version Volume group - case-insensitive
volume_group = validator.add_argument("-V", "--volume", help="The version volume (or scale) used for the "
                                                             "testing environment. Default is 100. The single "
                                                             "version volume is defined as 1 node, the small volume is"
                                                             "defined as 10 nodes, the medium volume is 100 nodes, "
                                                             "large is 1000 nodes, and huge is 10000 nodes.",
                                      default="medium",
                                      type=check_version_volume)
# Version Density group
version_density_group = validator.add_argument_group("Version Density", "The version density to use for "
                                                                        "the simulation. Default is uniformly "
                                                                        "distributed.")
version_density_exclusive_group = version_density_group.add_mutually_exclusive_group()  # Make this group not required.
version_density_exclusive_group.add_argument("-l", "--linear", help="Linear version density. The "
                                                                    "slope should be between -2 and 2, inclusive.",
                                             metavar="slope", type=check_valid_linear_slope)
version_density_exclusive_group.add_argument("-b", "--bigheadlongtail", help="Big Head Long Tail version "
                                                                             "density. Generates a reciprocal "
                                                                             "(or log-uniform) distribution as the "
                                                                             "probability density function. The"
                                                                             "parameter must be a positive number that "
                                                                             "is not equal to one. The density "
                                                                             "function is "
                                                                             "f(x, a) = 1/[(1 + (a-1)*x) ln(a)], "
                                                                             "where 'a' is the shape parameter.",
                                             type=check_valid_bhlt_slope, metavar="shape_param")
version_density_exclusive_group.add_argument("-m", "--multipeak", help="""Multipeak is a weighted mixture of normal 
                                                                       distributions. Each normal distribution will 
                                                                       be marked by weight, mean, and standard 
                                                                       deviation. Weights don't need to add to one, 
                                                                       though they will be scaled down in proportion 
                                                                       to the weight. The params will be parsed by 
                                                                       weight, mean, then standard deviation. So for 
                                                                       example, if you want a mixture distribution 
                                                                       with 50%% chance of coming from a normal 
                                                                       distribution with mean 0 and standard deviation 
                                                                       20, and 50%% chance of coming from a normal 
                                                                       distribution with mean 100 and standard 
                                                                       deviation 30, then you would enter 
                                                                       '-m 0.5 0 20 -m 0.5 100 30' or
                                                                       '--multipeak 0.5 0 20 --multipeak 0.5 100 30'.
                                                                       """,
                                             metavar=("weight", "mean", "sd"), nargs=3, action="append",
                                             type=check_float)

validator.add_argument("-n", "--number-of-iterations", help="Number of iterations. Default is 10. Note "
                                                            "that this only affects the operations done after storing, "
                                                            "which means the number of iterations for the storage "
                                                            "depends on the version volume.",
                       default=10, type=check_positive_int, metavar="iterations", dest="iterations")
validator.add_argument("-O", "--operations", help="""The operation to use. Options are 'first' for get 
                                                 first, 'latest' for get latest, 'time' for get at uniformly 
                                                 distributed time T, 'nth' for get Nth node, and 'list' for list all. 
                                                 By default, all operations are included in this simulation and default
                                                 to the number of iterations (with the exception of 'list', which will
                                                 always happen 10 times). Multiple operation choices are allowed. For 
                                                 instance, '-O list nth' will simulate the nth and list operations.
                                                 Repeated operations are not allowed.""",
                       choices=operation_choices, nargs='*', action='extend')
validator.add_argument("-v", "--verbose", help="Prints detailed output.", action="store_true")
validator.add_argument("-i", "--interval", help="""The time interval for simulation.
Default is 1000. The interval will not be used in the multipeak distribution.""",
                       type=check_greater_than_zero, default=1000, metavar="seconds")


def post_validate(args):
    """
    Does a post-validation check to ensure proper formats.
    """
    if args.tempexp and not check_greater_than_one(args.tempexp[0]):
        print("Base must be greater than one.", file=stderr)
        exit(2)
    elif params := args.multipeak:
        for param in params:
            if param[0] < 0:
                print("All weights must be positive.", file=stderr)
                exit(3)
    if ops := args.operations:
        if len(ops) != len(set(ops)):
            print("Options must be unique.", file=stderr)
            exit(4)
