import streamlit as st


if __name__ == '__main__':
    HOME = st.Page("pages/1_Home.py", icon=":material/home:")
    SELECT_POLICIES = st.Page("pages/2_Select_Policies.py", icon=":material/graph_1:")
    SUMMARY_REPORT = st.Page("pages/3_Summary_Report.py", icon=":material/summarize:")  # ":material/analytics:"
    SPACETIME_TRADEOFF = st.Page("pages/4_Space_Time_Tradeoff.py", icon=":material/access_time:")
    POLICY_GROWTH = st.Page("pages/5_Policy_Growth_Rate.py", icon=":material/trending_up:")
    COST_MAP = st.Page("pages/6_Cost_Map.py", icon=":material/paid:")
    ITERATION_LEVEL = st.Page("pages/7_Iteration_Level_Analysis.py", icon=":material/analytics:")

    pg = st.navigation({"Home": [HOME],
                        "Reports": [SELECT_POLICIES, SUMMARY_REPORT, SPACETIME_TRADEOFF, POLICY_GROWTH,
                                    COST_MAP, ITERATION_LEVEL]}, expanded=True)
    pg.run()
