import streamlit as st

if __name__ == '__main__':
    home = st.Page("pages/1_Home.py", icon=":material/home:")
    operations_report = st.Page("pages/2_Operations_Report.py", icon=":material/analytics:")
    spacetime_tradeoff = st.Page("pages/3_Space_Time_Tradeoff.py", icon=":material/access_time:")
    policy_growth = st.Page("pages/4_Policy_Growth_Rate.py", icon=":material/trending_up:")
    pg = st.navigation([home, operations_report, spacetime_tradeoff, policy_growth], expanded=True)
    pg.run()
