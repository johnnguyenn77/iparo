import streamlit as st

if __name__ == '__main__':
    home = st.Page("pages/1_Home.py", icon=":material/home:")
    operations_report = st.Page("pages/2_Operations_Report.py", icon=":material/settings:")
    spacetime_tradeoff = st.Page("pages/3_Space_Time_Tradeoff.py", icon=":material/access_time:")
    pg = st.navigation([home, operations_report, spacetime_tradeoff], expanded=True)
    pg.run()
