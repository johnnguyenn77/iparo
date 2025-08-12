import streamlit as st
from streamlit import session_state as ss

from components.utils import POLICY_GROUPS, POLICY_GROUP_COMBINATIONS


def policy_visualization_settings():
    st.title("Policy Visualization Settings")
    st.text("Before accessing any report page, please select the policies to use. You may "
            "select one policy.")
    groups = set(POLICY_GROUPS.keys())
    with st.form('policy_group_form'):
        st.markdown("### Step 1: Select Policy Group")
        st.text("Please select a policy group for this step.")
        policy_group = st.selectbox("Select Policy Group", groups)
        policy_group_submitted = st.form_submit_button()
    if policy_group_submitted:
        params = [param for policy, param in POLICY_GROUP_COMBINATIONS if policy == policy_group]
        ss['policy_group'] = policy_group
        ss['policy_group_params'] = params
    if 'policy_group' in ss:
        with st.form('policy_form'):
            # Pass 1: Get all names of files
            st.markdown("### Step 2: Select Policy")
            policy_group_param = st.selectbox("Select Policy Parameter", ss['policy_group_params'])
            node_number = st.slider("Number of Nodes", 1, 20)
            policy_submitted = st.form_submit_button()
        if policy_submitted:
            ss['policy_group_param'] = policy_group_param
            ss['node_num'] = node_number
            st.switch_page("pages/10_Policy_Visualization.py")


if __name__ == '__main__':
    policy_visualization_settings()
