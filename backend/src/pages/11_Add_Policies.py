import streamlit as st
from streamlit import session_state as ss

from components.PolicyEditor import PolicyEditor
from components.utils import POLICY_GROUP_NAMES
from simulation.LinkingStrategy import LinkingStrategy


def get_policy(policy: LinkingStrategy, policy_args: list[str]):
    n = len(ss['policies'])
    policy_group = POLICY_GROUP_NAMES[ss['policy_group']]
    if len(policy_args) == 2:
        ss['policies'].add((" ".join(policy_args), str(policy), policy_group, policy_args[1]))
    elif len(policy_args) == 3:
        # Temporally exponential
        ss['policies'].add((" ".join(policy_args), str(policy), policy_group,
                            "Base-" + policy_args[1] + ", " + policy_args[2] + " Seconds"))
    else:  # No policy arguments
        ss['policies'].add((" ".join(policy_args), str(policy), policy_group, "None"))

    if len(ss['policies']) == n:  # Duplicate error message
        st.error("Failed to add policy because it is a duplicate. Please try again.")
    else:
        ss['success_message'] = f"Successfully added policy: {str(policy)}"

        st.switch_page("pages/12_View_Environments.py")


def create_policies():
    if 'policies' not in ss:
        ss['policies'] = set()
    if 'success_message' in ss:
        del ss['success_message']

    policy_editor = PolicyEditor(get_policy)
    policy_editor.display("Select Policies")


if __name__ == '__main__':
    create_policies()
