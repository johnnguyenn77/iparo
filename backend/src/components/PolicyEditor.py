from enum import Enum
from typing import Callable, Any

import streamlit as st
from streamlit import session_state as ss

from components.utils import POLICY_GROUP_NAMES
from simulation.CommandLineParser import CommandLineParser
from simulation.CommandLineValidator import post_validate, validator
from simulation.LinkingStrategy import LinkingStrategy


class PolicyEditor:

    def __init__(self, on_submit: Callable[[LinkingStrategy, list[str]], None]):
        """
        :param on_submit: The callback after the forms are submitted.
        """
        self.on_submit = on_submit
        self.policy_params: list[str] = []
        self.policy_submitted = False
        self.params = {}
        if 'stage' not in ss:
            ss['stage'] = 0

    def set_stage(self, i: int):
        ss['stage'] = i

    def display(self, title: str = "Select Policy"):
        st.title(title)
        groups = set(POLICY_GROUP_NAMES.keys())
        with st.form('policy_group_form'):
            st.subheader("Select Policy Group")
            st.text("Please select a policy group for this step.")
            st.selectbox("Select Policy Group", groups, format_func=POLICY_GROUP_NAMES.get,
                         key="policy_group")
            st.form_submit_button(on_click=self.set_stage, args=(1,))
        if ss['stage'] > 0:
            policy_group = ss['policy_group']
            if policy_group not in ['single', 'comprehensive']:
                with st.form('policy_param_form'):
                    st.subheader("Select Policy Parameters")
                    if policy_group == 'tempexp':
                        st.number_input("Enter Base (Greater than 1)", min_value=1.01,
                                        step=0.01, value=2.0, key="param1")
                        st.number_input("Enter Time Unit (seconds)", min_value=0.01,
                                        step=0.01, value=10.0, key="param2")
                    elif policy_group == 'seqexp':
                        st.number_input("Enter Base (Greater than 1)",
                                        min_value=1.001, step=0.001, value=2.0,
                                        format="%.3f", key="param1")
                    elif policy_group == 'tempmingap':
                        st.number_input("Enter Time Unit (seconds) ",
                                        min_value=0.001, step=0.001,
                                        value=200.0, format="%.3f", key="param1")
                    else:
                        st.number_input("Enter Parameter", min_value=1, value=2,
                                        key="param1")

                    ss['button'] = st.form_submit_button(on_click=self.set_stage, args=(2,))
            elif policy_group:
                ss['stage'] = 2
        if ss['stage'] > 1:
            raw_args = [f"--{ss['policy_group']}"]
            if 'param1' in ss:
                raw_args.append(str(ss['param1']))
                if 'param2' in ss:
                    raw_args.append(str(ss['param2']))
            try:
                args = validator.parse_args(raw_args)
                post_validate(args)
                parser = CommandLineParser(args)
                policy = parser.parse_policy()
                self.on_submit(policy, raw_args)
            except SystemExit:
                st.error("The arguments provided were invalid. Please try again.")
                ss['stage'] = 0
