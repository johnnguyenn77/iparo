import streamlit as st

if __name__ == '__main__':
    pg = st.navigation([st.Page("reports/home.py", title="Home", icon=":material/home:"),
                        st.Page("reports/operations_report.py", title="Operations Report",
                                icon=":material/settings:")])

    pg.run()