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
    ADD_POLICIES = st.Page("pages/11_Add_Policies.py", icon=":material/add:")
    VIEW_ENVIRONMENTS = st.Page("pages/12_View_Environments.py", icon=":material/image:")
    ADD_VERSION_DENSITIES = st.Page("pages/13_Add_Version_Densities.py", icon=":material/image:")
    SIMULATION_WRITER_OUTPUT = st.Page("pages/14_Simulation_Writer_Output.py", icon=":material/image:")
    COST_DENSITY_MAP = st.Page("pages/15_Cost_Density_Map.py", icon=":material/image:")
    COST_CALCULATOR = st.Page("pages/16_Cost_Calculator.py", icon=":material/image:")
    RESILIENCE_REPORT = st.Page("pages/17_Resilience_Report.py", icon=":material/graph_1:")
    POLICY_GROWTH_HEATMAP = st.Page("pages/18_Policy_Growth_Rate_Heatmap.py", icon=":material/trending_up:")
    pg = st.navigation({"Home": [HOME],
                        "Settings": [GENERAL_SETTINGS, SELECT_POLICIES],
                        "Reports": [SUMMARY_REPORT, SPACETIME_TRADEOFF, POLICY_GROWTH,
                                    COST_MAP, ITERATION_LEVEL, COST_DENSITY_MAP, COST_CALCULATOR,
                                    RESILIENCE_REPORT, POLICY_GROWTH_HEATMAP],
                        "Visualization": [POLICY_VISUALIZATION_SETTINGS, POLICY_VISUALIZATION],
                        "Simulation (WIP)": [ADD_POLICIES, VIEW_ENVIRONMENTS, ADD_VERSION_DENSITIES, SIMULATION_WRITER_OUTPUT]

                        }, expanded=True)
    pg.run()
