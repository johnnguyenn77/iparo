import os
import sys

from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment
from simulation.CommandLineParser import CommandLineParser
from simulation.CommandLineValidator import validator, post_validate
from simulation.IPAROSimulation import IPAROSimulation

if __name__ == '__main__':
    user_args = sys.argv[1:]

    # Verifier does most of the validation.
    args = validator.parse_args(user_args)
    # And we also post-validate our args.
    post_validate(args)
    # Parse command line input
    parser = CommandLineParser(args)

    policy = parser.parse_policy()
    volume = parser.parse_volume()
    operations = parser.parse_operations()
    density = parser.parse_density()
    iterations = parser.parse_iterations()
    verbose = parser.parse_verbosity()
    output_dir = parser.parse_output_directory()

    env = IPAROSimulationEnvironment(policy, volume, density, operations, verbose, iterations)
    os.chdir(env.output_dir)
    sim = IPAROSimulation(env)
    sim.run()
