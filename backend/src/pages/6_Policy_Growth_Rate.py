from components.CheckboxGroup import CheckboxGroup
from components.LayeredBoxPlot import LayeredBoxPlot
from components.utils import *
import streamlit as st
from streamlit import session_state as ss


def display_chart(df: pd.DataFrame, title: str, y_title: str, log_scale: bool):
    tabs = st.tabs(["Results By Scale 📈", "Results by Policy 📈", "Summary Data 🔢"])
    display_index = ['Policy', 'Scale', 'Density']
    with tabs[0]:
        plot1 = LayeredBoxPlot(df, title, y_title,
                               x="Policy:O", color="Policy:O",
                               log_scale=log_scale, column="Scale:O")
        plot1.display()
    with tabs[1]:
        plot2 = LayeredBoxPlot(df, title, y_title, x="Scale:O", color="Policy:O", log_scale=log_scale, column="Policy:O")
        plot2.display()
    with tabs[2]:
        st.dataframe(df.set_index(display_index))


def policy_growth_rate():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    st.title("Policy Growth Rate")
    log_scale = ss['log_scale']
    policies_selected = ss['selected_policies']
    density = ss['density']
    time_retrieval_df: pd.DataFrame = get_summary_data(policies_selected, density, "Time")
    nth_retrieval_df: pd.DataFrame = get_summary_data(policies_selected, density, "Nth")
    store_df: pd.DataFrame = get_summary_data(policies_selected, density,
                                              "Store", actions=[Action.LINKS])
    store_retrievals_df: pd.DataFrame = get_summary_data(policies_selected, density, "Store")
    st.header("Storage")
    st.subheader("Link Storage Memory Performance")
    display_chart(store_df, "IPFS Storage Memory Performance", "Number of Links Per IPARO",
                  log_scale)
    st.subheader("IPFS Storage Time Performance")
    display_chart(store_retrievals_df, "IPFS Storage Time Performance", "Number of IPFS Retrieves",
                  log_scale)
    st.header("Retrieval")
    st.subheader("Retrieval by Time")
    display_chart(time_retrieval_df, "IPFS Time Retrieval Performance", "Number of IPFS Retrieves",
                  log_scale)
    st.subheader("Retrieval by Nth")
    display_chart(nth_retrieval_df, "IPFS Nth Retrieval Performance", "Number of IPFS Retrieves",
                  log_scale)


if __name__ == '__main__':
    policy_growth_rate()
