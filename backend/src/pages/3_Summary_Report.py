from streamlit import session_state as ss
import streamlit as st


def summary_report():
    if 'selected_policies' not in ss:
        st.switch_page("pages/2_Select_Policies.py")

    # Here, we assume that the user already selected a summary report.


if __name__ == '__main__':
    summary_report()