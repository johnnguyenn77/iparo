import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit import session_state as ss

from components.utils import POLICY_GROUP_NAMES, DENSITY_NAMES
from simulation.CommandLineParser import CommandLineParser
from simulation.CommandLineValidator import validator, post_validate
from simulation.TimeUnit import TimeUnit
from simulation.VersionDensity import LinearVersionDensity, VersionGenerator, MultipeakVersionDensity, \
    UniformVersionDensity, BigHeadLongTailVersionDensity


def set_stage(stage: int):
    ss['stage'] = stage


def reset_density():
    ss['stage'] = 3
    if 'visualization_density' in ss:
        del ss['visualization_density']
    if 'density_parameters' in ss:
        del ss['density_parameters']


def policy_visualization_settings():
    st.title("Policy Visualization Settings")
    st.text("Before accessing the visualization page, please select an environment and a policy.")
    groups = set(POLICY_GROUP_NAMES.keys())
    if 'stage' not in ss:
        ss['stage'] = 0

    with st.form('density-group'):
        st.header("Step 1: Select Environment")
        st.subheader("Step 1a: Select Density Group")
        density_group = st.selectbox("Density", DENSITY_NAMES, format_func=DENSITY_NAMES.get,
                                     help="Version density to be displayed.", index=3)

        st.form_submit_button(on_click=set_stage, args=(1,))
    if ss['stage'] > 0:
        with st.form("density"):
            st.subheader("Step 1b: Select Density Parameters")
            ss['visualization_density_group'] = density_group
            # Call density parameters as a dynamic type
            if density_group == 'linear':
                interval = st.number_input("Interval (Seconds)", min_value=0.01, value=1000.0)
                density_parameters = st.slider("Choose Slope", min_value=-2.0, max_value=2.0, step=0.01,
                                               help="The slope of the probability mass function.")
                ss['visualization_density'] = LinearVersionDensity(density_parameters, interval)
            elif density_group == 'bhlt':
                interval = st.number_input("Interval (Seconds)", min_value=0.01, value=1000.0)
                is_reversed = st.selectbox("Choose Direction of Head", [False, True],
                                           format_func=lambda x: "Right" if x else "Left")
                density_parameter = st.number_input("Choose Shape Parameter", min_value=1.001, step=0.001, value=20.0,
                                                    format="%.3f",
                                                    help="The shape parameter of the scaled and shifted "
                                                         "log-uniform distribution.")
                shape_parameter = (1 / density_parameter) if is_reversed else density_parameter
                ss['visualization_density'] = BigHeadLongTailVersionDensity(shape_parameter, interval)
            elif density_group == 'multipeak':
                df = pd.DataFrame(columns=["Probability Weight", "Mean", "Standard Deviation"])
                st.session_state['density_parameters'] = st.data_editor(df, key="editor", column_config={
                    "Probability Weight": st.column_config.NumberColumn(min_value=0.0),
                    "Mean": st.column_config.NumberColumn(),
                    "Standard Deviation": st.column_config.NumberColumn(min_value=0.0)},
                                                                        num_rows="dynamic")
                weights: pd.Series = st.session_state['density_parameters']['Probability Weight']
                distributions: pd.DataFrame = st.session_state['density_parameters'].iloc[:, 1:]
                ss['visualization_density'] = MultipeakVersionDensity(weights=weights.to_numpy(dtype=np.float64),
                                                                      distributions=distributions.to_numpy(
                                                                          dtype=np.float64))
            else:
                interval = st.number_input("Interval (Seconds)", min_value=0.01, value=1000.0)
                ss['visualization_density'] = UniformVersionDensity(interval)

            st.form_submit_button(on_click=set_stage, args=(2,))

        st.button("Clear Density", on_click=reset_density)
    if ss['stage'] > 1:
        try:
            density = ss['visualization_density']
            generator = VersionGenerator(density)
            iparos = generator.generate(1000)
            first_iparo = iparos[0]
            timestamps = [(iparo.timestamp - first_iparo.timestamp) / TimeUnit.SECONDS for iparo in iparos]
            with st.form('confirm'):
                st.subheader("Step 1c: Confirm Version Density")
                st.text("Note: Version Density histograms may change from time to time, and contains a sample of "
                        "1000 IPAROs. The timestamps are also measured relative to the first node.")
                histogram = st.empty()
                with histogram:
                    histogram.altair_chart(alt.Chart(pd.DataFrame({"Timestamp": timestamps})).mark_bar().encode(
                        x=alt.X("Timestamp:Q", title="Timestamp (Seconds)", bin=True),
                        y=alt.Y("Timestamp:Q", title="Number of IPAROs (out of 1000)", aggregate="count")
                    ))

                st.form_submit_button(on_click=set_stage, args=(3,))
        except ValueError:
            st.error("Please enter valid parameters for the version density.")

    if ss['stage'] > 2:
        with st.form("node_number"):
            st.subheader("Step 1d: Set Node Number")
            ss['node_num'] = st.slider("Number of Nodes", 1, 20, 10)
            st.form_submit_button(on_click=set_stage, args=(4,))

    if ss['stage'] > 3:
        with st.form('policy_group_form'):
            st.header("Step 2: Select Policy")
            st.subheader("Step 2a: Select Policy Group")
            st.text("Please select a policy group for this step.")
            ss['policy_group'] = st.selectbox("Select Policy Group", groups, format_func=POLICY_GROUP_NAMES.get)
            st.form_submit_button(on_click=set_stage, args=(5,))

    if ss['stage'] > 4:
        if ss['policy_group'] not in ['single', 'comprehensive']:
            with st.form('policy_param_form'):
                # Pass 1: Get all names of files
                st.subheader("Step 2b: Select Policy Parameters")
                if ss['policy_group'] == 'tempexp':
                    ss['policy_param_1'] = st.number_input("Enter Base (Greater than 1)", min_value=1.01, step=0.01,
                                                           value=2.0, format="%.2f")
                    ss['policy_param_2'] = st.number_input("Enter Time Unit (seconds)", min_value=0.001, step=0.001,
                                                           value=10.0, format="%.3f")
                else:
                    if ss['policy_group'] == 'seqexp':
                        ss['policy_param_1'] = st.number_input("Enter Base (Greater than 1)", min_value=1.001,
                                                               step=0.001, value=2.0, format="%.3f")
                    elif ss['policy_group'] == 'tempmingap':
                        ss['policy_param_1'] = st.number_input("Enter Time Unit (seconds) ", min_value=0.001,
                                                               step=0.001, value=200.0, format="%.3f")
                    else:
                        ss['policy_param_1'] = st.number_input("Enter Parameter", min_value=1, value=2)
                    ss['policy_param_2'] = None

                st.form_submit_button(on_click=set_stage, args=(6,))
        elif 'policy_group' in ss:
            ss['policy_param_1'] = None
            ss['policy_param_2'] = None
            ss['stage'] = 6
        else:
            ss['stage'] = 5

    if ss['stage'] == 5 and 'policy_group' in ss and ss['policy_group'] in ['single', 'comprehensive']:
        ss['stage'] = 6

    if ss['stage'] == 6:
        args_list = [f"--{ss['policy_group']}"]
        param1 = str(ss['policy_param_1'] or '')
        param2 = str(ss['policy_param_2'] or '')
        if param1:
            args_list.append(param1)
        if param2:
            args_list.append(param2)
        try:
            args = validator.parse_args(args_list)
            post_validate(args)
            parser = CommandLineParser(args)
            ss['policy'] = parser.parse_policy()
            with st.form('final'):
                st.success("You may now access the visualization. Press to continue")
                ss['submitted'] = st.form_submit_button()
        except SystemExit:
            st.error("Please check your parameters and try again.")

    if 'submitted' in ss and ss['submitted']:
        st.switch_page("pages/10_Policy_Visualization.py")


if __name__ == '__main__':
    policy_visualization_settings()
