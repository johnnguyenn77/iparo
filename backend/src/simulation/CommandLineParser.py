from sys import stderr

from simulation.LinkingStrategy import *
from simulation.VersionDensity import *


class CommandLineParser:

    def __init__(self, args):
        """
        Constructor with user input from command-line args.
        """
        # Will be a "namespace" of command-line arguments,
        # so think of this as a JSON object.
        self.args = args

    def parse_policy(self) -> LinkingStrategy:
        """
        Based on args provided, gets the policy.
        """
        args = self.args
        if args.single:
            return SingleStrategy()
        elif args.comprehensive:
            return ComprehensiveStrategy()
        elif k := args.previous:
            return KPreviousStrategy(k) if k != 1 else PreviousStrategy()
        elif n := args.sequniform:
            return SequentialUniformNPriorStrategy(n)
        elif k := args.random:
            return KRandomStrategy(k)
        elif s := args.seqmaxgap:
            return SequentialSMaxGapStrategy(s)
        elif base := args.seqexp:
            return SequentialExponentialStrategy(base)
        elif n := args.tempuniform:
            return TemporallyUniformStrategy(n)
        elif t := args.tempmingap:
            return TemporallyMinGapStrategy(t)
        elif t := tuple(args.tempexp):
            base, time_unit = t
            return TemporallyExponentialStrategy(base, time_unit)
        raise AssertionError("The policy cannot be parsed.")

    def parse_volume(self):
        """
        Parses version volume
        """
        return self.args.volume

    def parse_density(self) -> VersionDensity:
        """
        Parses version density.
        """
        args = self.args
        interval = args.interval
        key = args.densitykey

        if slope := args.linear:
            return LinearVersionDensity(slope, interval, key)
        elif slope := args.bigheadlongtail:
            return BigHeadLongTailVersionDensity(slope, interval, key)
        elif params := args.multipeak:
            # First pass: get the sum of weights.
            mixture_params = np.array(params)
            return MultipeakVersionDensity(mixture_params[:, 0], mixture_params[:, 1:])
        return UniformVersionDensity(interval, key)

    def parse_operations(self):
        """
        Parses the type of operations.
        """
        return self.args.operations if self.args.operations else ["first", "latest", "time", "nth", "list"]

    def parse_iterations(self):
        """
        Parses the number of iterations.
        """
        return self.args.iterations

    def parse_verbosity(self):
        """
        Parses whether the output is verbose.
        """
        return self.args.verbose

    def parse_recompute_storage(self):
        """
        Parses whether the storage operations is averaged among all iterations.
        """
        return self.args.store_average

    def parse_output_directory(self):
        """
        Parses the output directory.
        """
        return self.args.output
