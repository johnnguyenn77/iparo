import streamlit as st

if __name__ == '__main__':
    home = st.Page("pages/1_Home.py", icon=":material/home:")
    # operations_report = st.Page("pages/2_Operations_Report.py", icon=":material/analytics:")
    # policy_growth = st.Page("pages/4_Policy_Growth_Rate.py", icon=":material/trending_up:")
    spacetime_tradeoff = st.Page("pages/2_Space_Time_Tradeoff.py", icon=":material/access_time:")
    pg = st.navigation([home], expanded=True)
    pg.run()
