import streamlit as st
import altair as alt
from streamlit import session_state as ss

from components.LayeredBoxPlot import LayeredBoxPlot
from components.utils import Action, get_summary_data, DENSITIES, OP_TYPES, SCALES


def summary_report():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")

    st.title("Summary Report")
    st.header("Results")
    log_scale = ss['log_scale']
    for operation in OP_TYPES:
        ctr = st.container()
        policies = ss['selected_policies']
        density = ss['density']
        actions = [action for action in Action if action != Action.LINKS]
        scale = ss['scale']
        if operation == 'Store':
            actions.append(Action.LINKS)

        df_summary = get_summary_data(policies, density, operation, [scale], actions)
        with ctr:
            st.subheader(operation)
            plot = LayeredBoxPlot(df_summary, f"Overall Requirements - {operation}",
                                  "Number of Actions", "Policy:O", "Action:O", "Policy:O",
                                  log_scale)
            plot.display()


if __name__ == '__main__':
    summary_report()
