from typing import Callable
import streamlit as st
from streamlit import session_state as ss

from components.utils import DENSITY_NAMES
from simulation.CommandLineParser import CommandLineParser
from simulation.CommandLineValidator import validator, post_validate
from simulation.VersionDensity import *
import altair as alt
import pandas as pd


class VersionDensityEditor:

    def __init__(self, on_submit: Callable[[list[str]], None]):
        self.on_submit = on_submit
        self.group = None
        self.density = None
        if 'stage' not in ss:
            ss['stage'] = 0

    def set_stage(self, stage: int):
        ss['stage'] = stage

    def display(self):
        button_pressed = False
        with st.form('density-group'):
            st.subheader("Select Density Group")
            st.selectbox("Density Group", DENSITY_NAMES, format_func=DENSITY_NAMES.get,
                         key="density_group", help="Version density to be displayed.", index=3)

            st.form_submit_button(on_click=self.set_stage, args=(1,))
        if ss['stage'] > 0:
            with st.form("density"):
                st.subheader("Select Density Parameters")
                density_group = ss['density_group']
                if 'density_parameter' in ss:
                    del ss['density_parameter']
                # Call density parameters as a dynamic type
                if density_group == 'linear':
                    st.number_input("Interval (Seconds)", key="interval", min_value=0.01, value=1000.0)
                    ss["density_parameter"] = st.slider("Choose Slope", min_value=-2.0, max_value=2.0, step=0.01,
                              value=2.0, help="The slope of the probability mass function.")
                elif density_group == 'bhlt':
                    st.number_input("Interval (Seconds)", key="interval", min_value=0.01, value=1000.0)
                    st.selectbox("Choose Direction of Head", [False, True],
                                 format_func=lambda x: "Right" if x else "Left",
                                 key="is_reversed")
                    st.number_input("Choose Shape Parameter", min_value=1.001, step=0.001,
                                    value=20.0,
                                    format="%.3f",
                                    help="The shape parameter of the scaled and shifted "
                                         "log-uniform distribution.",
                                    key="density_parameter")
                elif density_group == 'multipeak':
                    df = pd.DataFrame(columns=["Probability Weight", "Mean", "Standard Deviation"])
                    ss['density_parameter'] = st.data_editor(df, key="editor", column_config={
                        "Probability Weight": st.column_config.NumberColumn(min_value=0.0),
                        "Mean": st.column_config.NumberColumn(),
                        "Standard Deviation": st.column_config.NumberColumn(min_value=0.0)},
                                   num_rows="dynamic")

                else:
                    st.number_input("Interval (Seconds)", key="interval", min_value=0.01, value=1000.0)

                st.text_input("Unique Key", key="density_key", help="Please provide a unique key for the density. "
                                                                    "Make sure that the key is also descriptive.")
                button_pressed = st.form_submit_button()
        if button_pressed:
            if 'density_key' not in ss or ss['density_key'] == "":
                st.error("Please add a unique key for your density.")
            else:
                with st.form('confirm'):
                    st.subheader("Confirm Version Density")
                    st.text("Note: Version Density histograms may change from time to time, and contains a sample of "
                            "1000 IPAROs. The timestamps are also measured relative to the first node. For multipeak "
                            "distributions, you may want to press the submit button again for the histogram to "
                            "properly display.")
                    args = []
                    match ss['density_group']:
                        case 'multipeak':
                            n_rows = ss['density_parameter'].shape[0]
                            ss['density_parameter'] = (ss['density_parameter'].dropna(how="any")
                                                       .sort_values(by=['Probability Weight', 'Mean',
                                                                        'Standard Deviation']))
                            n_rows_cleaned = ss['density_parameter'].shape[0]
                            args.append("-s")
                            if ss['density_parameter'].shape[0] == 0:
                                st.warning("There are no filled rows in your multipeak data; falling back to uniform "
                                           "density.")
                            elif n_rows != n_rows_cleaned:
                                st.warning("There are unfilled rows in your multipeak data; using only fully filled "
                                           "rows.")

                            for _, row in ss['density_parameter'].iterrows():
                                args.append("-m")
                                args.append(str(row['Probability Weight']))
                                args.append(str(row['Mean']))
                                args.append(str(row['Standard Deviation']))
                        case 'uniform':
                            args = ["-s", "-i", str(ss['interval'])]
                        case 'linear':
                            args = ["-s", "-l", str(ss['density_parameter']), "-i", str(ss['interval'])]
                        case 'bhlt':
                            density_parameter = ((1 / ss['density_parameter']) if ss['is_reversed']
                                                 else ss['density_parameter'])
                            args = ["-s", "-b", str(density_parameter), "-i", str(ss['interval'])]
                        case _:
                            st.warning("Unknown Version Density, switching to Uniform.")
                            args = ["-s", "-i", str(ss['interval'])]
                    try:
                        namespace = validator.parse_args(args)
                        post_validate(namespace)
                        parser = CommandLineParser(namespace)
                        density = parser.parse_density()
                        generator = VersionGenerator(density)
                        iparos = generator.generate(1000)
                        first_iparo = iparos[0]
                        timestamps = [(iparo.timestamp - first_iparo.timestamp) / TimeUnit.SECONDS for iparo in iparos]
                        histogram = st.empty()
                        ss['args'] = args[1:]
                        with histogram:
                            histogram.altair_chart(alt.Chart(pd.DataFrame({"Timestamp": timestamps})).mark_bar().encode(
                                x=alt.X("Timestamp:Q", title="Timestamp (Seconds)", bin=True),
                                y=alt.Y("Timestamp:Q", title="Number of IPAROs (out of 1000)", aggregate="count")
                            ))
                        st.form_submit_button("Confirm", on_click=self.set_stage, args=(2,))
                    except SystemExit as e:
                        st.error("Invalid arguments: " + str(e))
        if ss['stage'] > 1:
            self.on_submit(ss['args'])
