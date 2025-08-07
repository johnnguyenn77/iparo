from components.CheckboxGroup import CheckboxGroup
from components.LayeredBoxPlot import LayeredBoxPlot
from components.utils import *
import streamlit as st
from streamlit import session_state as ss


def policy_growth_rate():
    if 'selected_policies' not in ss:
        st.switch_page("results/2_Select_Policies.py")
    st.title("Policy Growth Rate")
    error_message = st.empty()
    policies_selected = ss['selected_policies']
    with st.form('form'):
        st.header("Select Environment")
        densities_checkbox_group = CheckboxGroup(DENSITIES, help=DENSITIES_HELP)
        densities_checkbox_group.display()
        log_scale = st.checkbox("Logarithmic Scale", help="Displays the graphs with a symmetric log-scale x-axis and "
                                                          "y-axis.")
        submitted = st.form_submit_button()
        
    if submitted:
        listed_densities = densities_checkbox_group.get_value()
        if not listed_densities:
            error_message.error("Please select at least one density.")
        n_policies_selected = policies_selected.shape[0]
        time_retrieval_df = get_summary_data(policies_selected, listed_densities, "Time")
        nth_retrieval_df = get_summary_data(policies_selected, listed_densities, "Nth")
        store_df = get_summary_data(policies_selected, listed_densities,
                                    "Store", actions=[Action.LINKS])
        store_retrievals_df = get_summary_data(policies_selected, listed_densities, "Store")

        st.header("Store Operations")
        st.subheader("Link Storage Performance")
        plot_store_links = LayeredBoxPlot(store_df, "IPFS Storage Performance - Links", "Policy:N",
                                          "Link Count Per Node", log_scale=log_scale, n=n_policies_selected)
        plot_store_links.display()
    
        st.subheader("IPFS Retrieval Operations Requirements")
        plot_store_retrievals = LayeredBoxPlot(store_retrievals_df, "IPFS Storage Performance - Retrievals Per "
                                                                    "Store Operation", "Policy:N",
                                               "IPFS Retrievals Per Store Operation",
                                               log_scale=log_scale, n=n_policies_selected)
        plot_store_retrievals.display()
    
        st.header("IPFS Retrieval Performance")
        st.subheader("Time Retrieval")
        plot_retrieve_time = LayeredBoxPlot(time_retrieval_df, "IPFS Time Retrieval Performance",
                                            "Policy:N",
                                            "IPFS Retrievals", log_scale=log_scale, n=n_policies_selected)
        plot_retrieve_time.display()
        st.subheader("Nth Retrieval")
        plot_retrieve_nth = LayeredBoxPlot(nth_retrieval_df, "IPFS Nth Retrieval Performance", "Policy:N",
                                           "IPFS Retrievals", log_scale=log_scale, n=n_policies_selected)
        plot_retrieve_nth.display()


if __name__ == '__main__':
    policy_growth_rate()
