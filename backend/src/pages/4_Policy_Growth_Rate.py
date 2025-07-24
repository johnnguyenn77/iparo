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
        listed_policies = policy_group.get_value()
        listed_densities = density_group.get_value()
        if not listed_policies or not listed_densities:
            error_message.error("You must select at least one linking policy and one version density to view "
                                "growth rates.")
        else:
            time_retrieval_df = get_summary_data(listed_policies, listed_densities, "Time")
            nth_retrieval_df = get_summary_data(listed_policies, listed_densities, "Nth")
            store_df = get_summary_data(listed_policies, listed_densities, "Store", col_index=5)
            store_retrievals_df = get_summary_data(listed_policies, listed_densities, "Store")

            width = 45 * len(listed_policies)
            plot_store_links = LayeredBoxPlot(store_df, "IPFS Storage Performance - Links", "Policy:N",
                                              "Link Count Per Node", log_scale=log_scale)
            plot_store_links.set_width(width)
            plot_store_links.display()

            plot_store_retrievals = LayeredBoxPlot(store_retrievals_df, "IPFS Storage Performance - Links",
                                                   "Policy:N", "IPFS Retrievals Per Store Operation",
                                                   log_scale=log_scale)
            plot_store_retrievals.set_width(width)
            plot_store_retrievals.display()

            plot_retrieve_time = LayeredBoxPlot(time_retrieval_df, "IPFS Time Retrieval Performance", "Policy:N",
                                                "IPFS Retrievals", log_scale=log_scale)
            plot_retrieve_time.set_width(width)
            plot_retrieve_time.display()

            plot_retrieve_nth = LayeredBoxPlot(nth_retrieval_df, "IPFS Time Retrieval Performance", "Policy:N",
                                               "IPFS Retrievals", log_scale=log_scale)
            plot_retrieve_nth.set_width(width)
            plot_retrieve_nth.display()


if __name__ == '__main__':
    policy_growth_rate()
