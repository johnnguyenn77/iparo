from typing import Literal

import pandas as pd
import streamlit as st
import altair as alt

from components.CheckboxGroup import CheckboxGroup
from components.LayeredBoxPlot import LayeredBoxPlot
from components.utils import *


def policy_growth_rate():
    error_message = st.empty()

    policy_group = CheckboxGroup(POLICIES, "Choose your Linking Policies",
                                 help=POLICIES_HELP)

    density_help = {"BHLT": "Big Head Long Tail, which is a scaled and shifted loguniform distribution with "
                            "20 as its parameter.",
                    "Linear": "A distribution where the later nodes are more densely distributed "
                              "than the earlier nodes.",
                    "Multipeak": ("A mixture of two normal distributions, one with a mean "
                                  "of 0 seconds and a standard deviation of 30 seconds, and "
                                  "the other with a mean of 100 seconds and a standard deviation "
                                  "of 40 seconds.")}
    density_group = CheckboxGroup(DENSITIES, "Choose your Version Densities",
                                  help=density_help)

    with st.form('form'):
        # Pass 1: Get all names of files
        policy_group.display()
        density_group.display()
        log_scale = st.checkbox("Logarithmic Scale", help="Enables both the x-axis and y-axis to be displayed with "
                                                          "a symmetric logarithmic scale.")
        submitted = st.form_submit_button()

    if submitted:
        # .transpose().reset_index().rename(
        #     columns={"index": "Status", "25%": "q1", "50%": "median", "75%": "q3"}).replace(np.nan, 0).astype(
        #     {"count": int, "min": int, "max": int})
        listed_policies = policy_group.get_value()
        if not listed_policies:
            error_message.error("You must select at least one linking policy to view.")
        else:
            time_retrieval_df = get_summary_data(listed_policies, "Time")
            nth_retrieval_df = get_summary_data(listed_policies, "Nth")
            store_df = get_summary_data(listed_policies, "Store", col_index=5)
            store_retrievals_df = get_summary_data(listed_policies, "Store")
            
            plot_store_links = LayeredBoxPlot(store_df, "IPFS Storage Performance - Links", "Policy:N",
                                              "Link Count Per Node", log_scale=log_scale)
            plot_store_links.display()

            plot_store_retrievals = LayeredBoxPlot(store_retrievals_df, "IPFS Storage Performance - Links",
                                                   "Policy:N", "IPFS Retrievals Per Store Operation",
                                                   log_scale=log_scale)
            plot_store_retrievals.display()

            plot_retrieve_time = LayeredBoxPlot(time_retrieval_df, "IPFS Time Retrieval Performance", "Policy:N",
                                                "IPFS Retrievals", log_scale=log_scale)
            plot_retrieve_time.display()

            plot_retrieve_nth = LayeredBoxPlot(nth_retrieval_df, "IPFS Time Retrieval Performance", "Policy:N",
                                               "IPFS Retrievals", log_scale=log_scale)
            plot_retrieve_nth.display()

        #     store_df.set_index(["Policy", "Density", "Statistic"], inplace=True)
        #     retrieval_nth_df = pd.concat(partial_nth_retrieval_dfs)
        #     retrieval_nth_df.set_index(["Policy", "Density", "Statistic"], inplace=True)
        #     retrieval_time_df = pd.concat(partial_time_retrieval_dfs)
        #     retrieval_time_df.set_index(["Policy", "Density", "Statistic"], inplace=True)
        #
        #     st.header("Output")
        #     # Next, visualize.
        #     tab1, tab2 = st.tabs(["Results 📈", "Data 🔢"])
        #     scale_type: Literal['symlog', 'identity'] = "symlog" if log_scale else "identity"
        #     with tab1:
        #         chart = alt.Chart(store_retrieve_df,
        #                           title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval Performance - "
        #                                                 f"{aggregate_names[statistic]}")).mark_point().encode(
        #             x=alt.X("Links:Q", title="IPFS Links Per Node").scale(type=scale_type),
        #             y=alt.Y("IPFS Retrieve (Time):Q").scale(type=scale_type),
        #             color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400)),
        #             shape=alt.Shape("Density:O", legend=alt.Legend(labelLimit=400))
        #         )
        #         st.altair_chart(chart)
        #         chart2 = alt.Chart(store_retrieve_df,
        #                            title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval Performance - "
        #                                                  f"{aggregate_names[statistic]}")).mark_point().encode(
        #             x=alt.X("Links:Q", title="IPFS Links Per Node").scale(type=scale_type),
        #             y=alt.Y("IPFS Retrieve (Sequence Number):Q").scale(type=scale_type),
        #             color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400)),
        #             shape=alt.Shape("Density:O", legend=alt.Legend(labelLimit=400)),
        #         )
        #         st.altair_chart(chart2)
        #     with tab2:
        #         st.dataframe(store_retrieve_df, hide_index=True)


if __name__ == '__main__':
    policy_growth_rate()
