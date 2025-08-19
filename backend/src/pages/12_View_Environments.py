import numpy as np
import pandas as pd
import streamlit as st
from streamlit import session_state as ss

from components.utils import POLICY_GROUP_NAMES


def simulate():
    errored = False
    if len(ss['policies']) == 0:
        errored = True
        st.error("Please have at least one policy to test.")
    if len(ss['densities']) == 0:
        errored = True
        st.error("Please have at least one version density to test.")
    if len(ss['volume_data']) == 0:
        errored = True
        st.error("Please have at least one version volume to test.")
    if ss['volume_data']['Chain Length'].nunique() != len(ss['volume_data']['Chain Length']):
        errored = True
        st.error("Please have ensure that all your chain lengths are unique.")
    if not errored:
        ss['simulate'] = True
        st.switch_page("pages/14_Simulation_Writer_Output.py")


def view_environments():
    if 'policies' not in ss:
        ss['policies'] = set()
    if 'densities' not in ss:
        ss['densities'] = {}
    if 'success_message' in ss:
        st.success(ss['success_message'])
        del ss['success_message']
    if 'stage' in ss:
        del ss['stage']
    st.title("View Environments")
    st.markdown("Note that each key will be considered as part of the file name. "
                "In fact, the file structure is `[Policy Group]/[Policy Param Key]/"
                "[Volume]-[Density Key]-[Operation Shorthand].csv`")
    st.header("Policies")
    policy_list = [[policy, POLICY_GROUP_NAMES[group], param_key, arg, False]
                   for arg, policy, group, param_key in ss['policies']]

    ss['policies_data'] = pd.DataFrame(policy_list, columns=["Name", "Policy Group", "Param Key", "Command-Line Args",
                                                             "Selected"])
    ss['policies_data'] = st.data_editor(ss['policies_data'], hide_index=True,
                                         disabled=["Name", "Policy Group", "Param Key", "Command-Line Args"])
    columns = st.columns(2)
    add_policy = columns[0].button("Add Policy")
    if add_policy:
        st.switch_page("pages/11_Add_Policies.py")
    delete_policy = columns[1].button("Delete Selected Policies")
    if delete_policy:
        policies = ss['policies_data']
        for i, row in policies.loc[policies['Selected']].iterrows():
            ss['policies'].remove((row['Command-Line Args'], row['Name']))
        ss['success_message'] = "Successfully deleted selected policies."
        st.rerun()

    st.header("Densities")
    densities_list = [[density_key, arg, False] for density_key, arg in ss['densities'].items()]
    ss['densities_data'] = pd.DataFrame(densities_list,
                                        columns=["Version Density Key", "Command-Line Args", "Selected"])
    ss['densities_data'] = st.data_editor(ss['densities_data'], hide_index=True,
                                          disabled=['Version Density Key', 'Command-Line Args'])
    columns = st.columns(2)
    add_density = columns[0].button("Add Density")
    delete_density = columns[1].button("Delete Density")
    if add_density:
        st.switch_page("pages/13_Add_Version_Densities.py")
    if delete_density:
        policies = ss['densities_data']
        for i, row in policies.loc[policies['Selected']].iterrows():
            del ss['densities'][row['Version Density Key']]
        ss['success_message'] = "Successfully deleted selected densities."
        st.rerun()

    st.header("Version Volumes")
    if 'volumes' not in ss:
        ss['volumes'] = pd.DataFrame({"Chain Length": pd.Series([10], dtype=np.int_)})
    ss['volume_data'] = st.data_editor(ss["volumes"], key="volume_editor", column_config={
        "Chain Length": st.column_config.NumberColumn(min_value=1)
    }, num_rows="dynamic")

    st.header("Other Settings")
    st.text("For parallel execution, please refer to the command-line application and the bash script for it.")
    st.number_input("Number of Iterations", min_value=1, value=10,
                    help="Number of iterations for each operation besides the store operation. "
                         "Number of iterations for the store operation are only affected by the "
                         "version volume.", key="iterations")
    st.checkbox("Verbose", help="Debugging output.", key="verbose")
    # ss['parallel'] = st.checkbox("Allow Parallel Computation", help="Allows a multiprocessing pool to expedite the "
    #                                                                 "simulation process. However, this may come with "
    #                                                                 "the risk of using up more memory.")
    simulation_pressed = st.button("Run Script")
    if simulation_pressed:
        simulate()


if __name__ == '__main__':
    view_environments()
