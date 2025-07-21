import os

import streamlit as st

from components.CheckboxGroup import CheckboxGroup
from components.utils import *


def spacetime_tradeoff():
    error_message = st.empty()

    policy_group = CheckboxGroup(POLICIES, "Choose your Linking Policies",
                                 help=POLICIES_HELP)
    density_group = CheckboxGroup(DENSITIES, "Choose your Version Densities",
                                  help={"BHLT": "Big Head Long Tail, which is a scaled loguniform distribution with "
                                                "20 as its parameter.",
                                        "Linear": "A distribution where the later nodes are more densely distributed "
                                                  "than the earlier nodes.",
                                        "Multipeak": ("A mixture of two normal distributions, one with a mean "
                                                      "of 0 seconds and a standard deviation of 30 seconds, and "
                                                      "the other with a mean of 100 seconds and a standard deviation "
                                                      "of 40 seconds.")})
    with st.form('form'):
        # Pass 1: Get all names of files
        policy_group.display()
        density_group.display()
        scale = st.selectbox("Select Scale", SCALES)
        submitted = st.form_submit_button()

    if submitted:
        listed_policies = policy_group.get_value()
        version_densities = density_group.get_value()
        if not listed_policies or not version_densities:
            error_message.error("You must select at least one linking policy and one version density to view.")
        else:
            pass


if __name__ == '__main__':
    spacetime_tradeoff()
