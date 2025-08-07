from components.CheckboxGroup import CheckboxGroup
from components.LayeredBoxPlot import LayeredBoxPlot
from components.utils import *
import streamlit as st
from streamlit import session_state as ss


def display_chart(df: pd.DataFrame, title: str, y_title: str, n_policies_selected: int, log_scale: bool):
    tabs = st.tabs(["Results By Scale 📈", "Results by Policy 📈", "Summary Data 🔢"])
    display_index = ['Policy', 'Scale', 'Density']
    with tabs[0]:
        plot1 = LayeredBoxPlot(df, title, y_title,
                               x="Policy:O", n_cols=len(SCALES), n=n_policies_selected,
                               column="Scale:O", row="Density:O", color="Policy:O",
                               log_scale=log_scale)
        plot1.display()
    with tabs[1]:
        plot2 = LayeredBoxPlot(df, title, y_title, x="Scale:O", column="Policy:O",
                               row="Density:O", color="Policy:O", log_scale=log_scale,
                               n=len(SCALES), n_cols=n_policies_selected)
        plot2.display()
    with tabs[2]:
        st.dataframe(df.set_index(display_index))


def policy_growth_rate():
    if 'selected_policies' not in ss:
        st.switch_page("pages/2_Select_Policies.py")
    st.title("Policy Growth Rate")
    error_message = st.empty()
    policies_selected = ss['selected_policies']
    with st.form('form'):
        st.header("Choose Environment")
        densities_checkbox_group = CheckboxGroup(DENSITIES, help=DENSITIES_HELP)
        densities_checkbox_group.display()
        st.markdown("#### Graph Display Options")
        log_scale = st.checkbox("Logarithmic Scale", help="Displays the graphs with a symmetric log-scale y-axis.")
        submitted = st.form_submit_button()

    if submitted:
        listed_densities = densities_checkbox_group.get_value()
        if not listed_densities:
            error_message.error("Please select at least one density.")
        n_policies_selected = policies_selected.shape[0]
        time_retrieval_df: pd.DataFrame = get_summary_data(policies_selected, listed_densities, "Time")
        nth_retrieval_df: pd.DataFrame = get_summary_data(policies_selected, listed_densities, "Nth")
        store_df: pd.DataFrame = get_summary_data(policies_selected, listed_densities,
                                                  "Store", actions=[Action.LINKS])
        store_retrievals_df: pd.DataFrame = get_summary_data(policies_selected, listed_densities, "Store")
        st.header("Storage")
        st.subheader("Link Storage Memory Performance")
        display_chart(store_df, "IPFS Storage Memory Performance", "Number of Links Per IPARO",
                      n_policies_selected, log_scale)
        st.subheader("IPFS Storage Time Performance")
        display_chart(store_retrievals_df, "IPFS Storage Time Performance", "Number of IPFS Retrieves",
                      n_policies_selected, log_scale)
        st.header("Retrieval")
        st.subheader("Retrieval by Time")
        display_chart(time_retrieval_df, "IPFS Time Retrieval Performance", "Number of IPFS Retrieves",
                      n_policies_selected, log_scale)
        st.subheader("Retrieval by Nth")
        display_chart(nth_retrieval_df, "IPFS Nth Retrieval Performance", "Number of IPFS Retrieves",
                      n_policies_selected, log_scale)


if __name__ == '__main__':
    policy_growth_rate()
