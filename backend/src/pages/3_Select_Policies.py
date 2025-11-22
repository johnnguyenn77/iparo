import streamlit as st
from streamlit import session_state as ss

from components.CheckboxGroup import CheckboxGroup
from components.utils import *


def select_policies():
    if 'density' not in ss:
        st.switch_page("pages/2_General_Settings.py")
    st.title("Select Policies")
    st.text("Before accessing any report page, please select the policies to use. You may "
            "select 1 to 10 policies.")
    error_message = st.empty()
    groups = POLICY_GROUPS.keys()
    lists = pd.DataFrame([[policy, param, False] for policy, param in POLICY_GROUP_COMBINATIONS],
                         columns=["Group", "Param", "Used"])
    with st.form('policy_group_form'):
        st.markdown("### Step 1: Select Policy Groups")
        st.text("Please select at least one policy group for this step.")
        policy_group = CheckboxGroup(groups)
        policy_group.display()
        policy_group_submitted = st.form_submit_button()
    if policy_group_submitted:
        if not policy_group:
            error_message.error("Please select at least one policy group.")
        else:
            ss['selected_policy_groups'] = lists[lists['Group'].isin(policy_group.get_value())]
    if 'selected_policy_groups' in ss:
        with st.form('policy_form'):
            # Pass 1: Get all names of files
            st.markdown("### Step 2: Select Policies")
            error_message_2 = st.empty()
            st.text("Please select 1-10 policies.")
            ss['selected_groups'] = st.data_editor(ss['selected_policy_groups'],
                                                   disabled=['Group', 'Param'],
                                                   hide_index=True)
            policies_submitted = st.form_submit_button()
            if policies_submitted:
                policy_group_selected: pd.DataFrame = ss['selected_groups']
                policies_selected: pd.DataFrame = policy_group_selected.loc[
                    policy_group_selected['Used'], ['Group', 'Param']]

                n_policies_selected = policies_selected.shape[0]
                if n_policies_selected == 0:
                    error_message_2.error("Please select at least one policy.")
                elif n_policies_selected > 10:
                    error_message_2.error("Please select no greater than ten policies.")
                else:
                    ss['selected_policies'] = policies_selected
                    ss['policy_names'] = []

                    for row in policies_selected.itertuples(index=False):
                        name = row[0]  # 0 corresponds to Group
                        if row[1] != 'None':  # 1 corresponds to Param
                            name = format_policy_params(name, row[1])
                        ss['policy_names'].append(name)

                    st.success("Success! Now you may enter any other page. Policies selected: " + ', '.join(ss['policy_names']))


if __name__ == '__main__':
    select_policies()
