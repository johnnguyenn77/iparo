import os

import streamlit as st
from streamlit import session_state as ss

from components.utils import RESULTS_FOLDER, POLICY_GROUP_NAMES
from simulation.CommandLineParser import CommandLineParser
from simulation.CommandLineValidator import validator
from simulation.IPAROSimulation import IPAROSimulation
from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment


if __name__ == '__main__':
    if 'simulate' not in ss:
        st.switch_page("pages/12_View_Environments.py")

    del ss['simulate']
    for policy_args, _, policy_group, subdir in ss['policies']:
        for _, density_row in ss['densities_data'].iterrows():
            for _, v in ss['volumes'].iterrows():
                density_key: str = density_row['Version Density Key']
                density_args = density_row['Command-Line Args']

                path = str(os.path.join(RESULTS_FOLDER, POLICY_GROUP_NAMES[policy_group], subdir))
                raw_args = f"{policy_args} {density_args} -V {v['Chain Length']} -k {density_key} -n {ss['iterations']}".split(" ")
                if ss['verbose']:
                    raw_args.append("-v")

                raw_args.extend(['-o', path])
                args = validator.parse_args(raw_args)
                parser = CommandLineParser(args)
                policy = parser.parse_policy()
                volume = parser.parse_volume()
                operations = parser.parse_operations()
                density = parser.parse_density()
                iterations = parser.parse_iterations()
                verbose = parser.parse_verbosity()
                output_dir = parser.parse_output_directory().strip()
                env = IPAROSimulationEnvironment(policy, volume, density, operations, path, verbose,
                                                 iterations)
                sim = IPAROSimulation(env)
                sim.run()
