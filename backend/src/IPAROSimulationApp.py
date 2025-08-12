import streamlit as st


if __name__ == '__main__':
    HOME = st.Page("pages/1_Home.py", icon=":material/home:")
    GENERAL_SETTINGS = st.Page("pages/2_General_Settings.py", icon=":material/settings:")
    SELECT_POLICIES = st.Page("pages/3_Select_Policies.py", icon=":material/graph_1:")
    SUMMARY_REPORT = st.Page("pages/4_Summary_Report.py", icon=":material/summarize:")
    SPACETIME_TRADEOFF = st.Page("pages/5_Space_Time_Tradeoff.py", icon=":material/access_time:")
    POLICY_GROWTH = st.Page("pages/6_Policy_Growth_Rate.py", icon=":material/trending_up:")
    COST_MAP = st.Page("pages/7_Cost_Map.py", icon=":material/paid:")
    ITERATION_LEVEL = st.Page("pages/8_Iteration_Level_Analysis.py", icon=":material/analytics:")
    POLICY_VISUALIZATION_SETTINGS = st.Page("pages/9_Policy_Visualization_Settings.py", icon=":material/settings:")
    POLICY_VISUALIZATION = st.Page("pages/10_Policy_Visualization.py", icon=":material/image:")
    pg = st.navigation({"Home": [HOME],
                        "Settings": [GENERAL_SETTINGS, SELECT_POLICIES],
                        "Reports": [SUMMARY_REPORT, SPACETIME_TRADEOFF, POLICY_GROWTH,
                                    COST_MAP, ITERATION_LEVEL],
                        "Visualization": [POLICY_VISUALIZATION_SETTINGS, POLICY_VISUALIZATION]}, expanded=True)
    pg.run()
