from typing import Literal

import pandas as pd
import streamlit as st
import altair as alt

from components.CheckboxGroup import CheckboxGroup
from components.utils import *


def spacetime_tradeoff():
    error_message = st.empty()

    policy_group = CheckboxGroup(POLICIES, "Choose your Linking Policies",
                                 help=POLICIES_HELP)

    density_help = {"BHLT": "Big Head Long Tail, which is a scaled loguniform distribution with "
                            "20 as its parameter.",
                    "Linear": "A distribution where the later nodes are more densely distributed "
                              "than the earlier nodes.",
                    "Multipeak": ("A mixture of two normal distributions, one with a mean "
                                  "of 0 seconds and a standard deviation of 30 seconds, and "
                                  "the other with a mean of 100 seconds and a standard deviation "
                                  "of 40 seconds.")}
    density_group = CheckboxGroup(DENSITIES, "Choose your Version Densities",
                                  help=density_help)

    aggregate_names = {"min": "Minimum", "25%": "1st Quartile", "50%": "Median",
                       "75%": "3rd Quartile", "max": "Maximum", "mean": "Mean"}
    with st.form('form'):
        # Pass 1: Get all names of files
        policy_group.display()
        density_group.display()
        scale = st.selectbox("Select Scale", SCALES)
        statistic = st.selectbox("Choose Aggregation Function", ["mean", "min", "25%", "50%", "75%", "max"],
                                 format_func=lambda x: aggregate_names[x])
        log_scale = st.checkbox("Logarithmic Scale", help="Enables both the x-axis and y-axis to be displayed with "
                                                          "a symmetric logarithmic scale.")
        submitted = st.form_submit_button()

    if submitted:
        listed_policies = policy_group.get_value()
        version_densities = density_group.get_value()
        if not listed_policies or not version_densities:
            error_message.error("You must select at least one linking policy and one version density to view.")
        else:
            partial_nth_retrieval_dfs = []
            partial_time_retrieval_dfs = []
            partial_store_dfs = []
            for policy_name in listed_policies:
                policy_filename = policy_name_to_file_name(policy_name)
                for density in version_densities:
                    filename_prefix = f"{RESULTS_FOLDER}/{policy_name}/{policy_filename}-{scale}-{density}"

                    # Statistic = 0, IPFS Retrieve = 4
                    partial_time_retrieval_df = pd.read_csv(f"{filename_prefix}-Time.csv",
                                                            skiprows=100, usecols=[0, 4])

                    partial_time_retrieval_df.columns = ["Statistic", "IPFS Retrieve (Time)"]
                    partial_time_retrieval_df["Policy"] = policy_name
                    partial_time_retrieval_df["Density"] = density

                    # Statistic = 0, IPFS Retrieve = 4
                    partial_nth_retrieval_df = pd.read_csv(f"{filename_prefix}-Nth.csv",
                                                           skiprows=100, usecols=[0, 4])

                    partial_nth_retrieval_df.columns = ["Statistic", "IPFS Retrieve (Sequence Number)"]
                    partial_nth_retrieval_df["Policy"] = policy_name
                    partial_nth_retrieval_df["Density"] = density

                    # Statistic = 0, Links = 5
                    partial_store_df = pd.read_csv(f"{filename_prefix}-Store.csv",
                                                   skiprows=SCALES_DICT[scale], usecols=[0, 5])
                    partial_store_df.columns = ["Statistic", "Links"]
                    partial_store_df["Policy"] = policy_name
                    partial_store_df["Density"] = density

                    partial_store_dfs.append(partial_store_df)
                    partial_time_retrieval_dfs.append(partial_time_retrieval_df)
                    partial_nth_retrieval_dfs.append(partial_nth_retrieval_df)

            store_df = pd.concat(partial_store_dfs)
            store_df.set_index(["Policy", "Density", "Statistic"], inplace=True)
            retrieval_nth_df = pd.concat(partial_nth_retrieval_dfs)
            retrieval_nth_df.set_index(["Policy", "Density", "Statistic"], inplace=True)
            retrieval_time_df = pd.concat(partial_time_retrieval_dfs)
            retrieval_time_df.set_index(["Policy", "Density", "Statistic"], inplace=True)

            st.header("Output")
            # Next, visualize.
            tab1, tab2 = st.tabs(["Results 📈", "Data 🔢"])
            scale_type: Literal['symlog', 'identity'] = "symlog" if log_scale else "identity"
            store_retrieve_df = store_df.join([retrieval_time_df, retrieval_nth_df]
                                              ).filter(like=statistic, axis=0).reset_index()
            with tab1:
                chart = alt.Chart(store_retrieve_df,
                                  title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval Performance - "
                                                        f"{aggregate_names[statistic]}")).mark_point().encode(
                    x=alt.X("Links:Q", title="IPFS Links Per Node").scale(type=scale_type),
                    y=alt.Y("IPFS Retrieve (Time):Q").scale(type=scale_type),
                    color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400)),
                    shape=alt.Shape("Density:O", legend=alt.Legend(labelLimit=400))
                )
                st.altair_chart(chart)
                chart2 = alt.Chart(store_retrieve_df,
                                   title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval Performance - "
                                                         f"{aggregate_names[statistic]}")).mark_point().encode(
                    x=alt.X("Links:Q", title="IPFS Links Per Node").scale(type=scale_type),
                    y=alt.Y("IPFS Retrieve (Sequence Number):Q").scale(type=scale_type),
                    color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400)),
                    shape=alt.Shape("Density:O", legend=alt.Legend(labelLimit=400)),
                )
                st.altair_chart(chart2)
            with tab2:
                st.dataframe(store_retrieve_df, hide_index=True)


if __name__ == '__main__':
    spacetime_tradeoff()
