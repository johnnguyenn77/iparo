import streamlit as st
from streamlit import session_state as ss

from components.LayeredBoxPlot import LayeredBoxPlot
from components.utils import Action, get_summary_data, DENSITIES, OP_TYPES, SCALES


def summary_report():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")

    st.title("Summary Report")
    st.header("Results")
    for operation in OP_TYPES:
        ctr = st.container()
        policies = ss['selected_policies']
        n_policies = len(ss['policy_names'])
        actions = [action for action in Action if action != Action.LINKS]
        if operation == 'Store':
            actions.append(Action.LINKS)

        df_summary = get_summary_data(policies, DENSITIES, operation, [scale], actions)
        with ctr:
            st.subheader(operation)
            plot = LayeredBoxPlot(df_summary, f'Linking Policy Performance - {operation}',
                                  "Number of Actions", "Policy:O", n_policies, len(actions),
                                  "Action:O", "Density:O", "Policy:O", log_scale)
            plot.display()


if __name__ == '__main__':
    summary_report()
