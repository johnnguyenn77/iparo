from typing import Literal

import pandas as pd
import streamlit as st
import altair as alt
from streamlit import session_state as ss

from components.utils import SCALES, OP_TYPES, get_summary_data, DENSITIES, Action, ACTIONS, ACTION_LIST, COLOR_SCHEME


def iteration_level_analysis():
    if 'selected_policies' not in ss:
        st.switch_page("pages/2_Select_Policies.py")

    st.title("Iteration-Level Analysis")
    st.markdown("**Warning**: The iteration-level analysis may take longer than the summary-level analysis since up "
                "to 10000 data points may be analyzed as opposed to roughly 8 for summary-level for each operation, "
                "especially for the Store action.")
    with st.form('form'):
        st.header("Choose Environment")
        scale = st.selectbox("Select Scale", SCALES)
        operation = st.selectbox("Select Operation", OP_TYPES)
        st.markdown("#### Graph Display Options")
        log_scale = st.checkbox("Logarithmic Scale", help="Displays the graphs with a symmetric log-scale y-axis.")
        submitted = st.form_submit_button()

    bar = st.empty()
    if submitted:
        st.header("Results")
        scale_type: Literal['identity', 'symlog'] = 'symlog' if log_scale else 'identity'
        for i, density in enumerate(DENSITIES):
            bar.progress(i / 4, text=f"Gathering data. Please wait... ({5 * i} / 20)")
            st.subheader(density)
            actions = [action for action in Action if action != Action.LINKS]
            if operation == 'Store':
                actions.append(Action.LINKS)

            summary: pd.DataFrame = get_summary_data(ss['selected_policies'], listed_densities=[density],
                                                     scales=[scale],
                                                     operation=operation, actions=actions,
                                                     analyze_all_iterations=True)
            bar.progress((5 * i + 1) / 20, text=f"Rendering charts. Please wait... ({5 * i + 1} / 20)")

            summary_long: pd.DataFrame = summary.melt(id_vars=["Policy", "Density", "Scale", "Iteration"],
                                                      var_name="Action", value_name="Action Count")
            tabs = st.tabs(['Iteration Results By Policy', 'Iteration Results By Action', 'Iteration Data'])
            title = alt.TitleParams(f'Linking Policy Performance - {operation}', anchor='middle')
            with tabs[0]:
                chart1 = alt.Chart(summary_long).mark_line(point=True, opacity=0.2).encode(
                    x=alt.X("Iteration:Q", title="Iteration Number"),
                    y=alt.Y(f"Action Count:Q", title="Operation Count", scale=alt.Scale(type=scale_type)),
                    color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                                    scale=alt.Scale(scheme=COLOR_SCHEME)),
                    opacity=alt.value(0.5),
                    tooltip=["Policy:O", alt.Tooltip("Iteration:Q", format=","),
                             alt.Tooltip("Action Count:Q", format=",")]
                ).properties(
                    width=200,
                    height=200
                ).facet(
                    column=alt.Column("Action:O", title="Type of Operation", sort=ACTION_LIST,
                                      header=alt.Header(orient="bottom")),
                    title=title
                )
                st.altair_chart(chart1)
                bar.progress((5 * i + 2) / 20, text=f"Rendering charts. Please wait... ({5 * i + 2} / 20)")
            with tabs[1]:
                chart2 = alt.Chart(summary_long).mark_line(point=True, opacity=0.2).encode(
                    x=alt.X("Iteration:Q", title="Iteration Number"),
                    y=alt.Y(f"Action Count:Q", title="Operation Count", scale=alt.Scale(type=scale_type)),
                    color=alt.Color("Action:O", legend=alt.Legend(labelLimit=400),
                                    scale=alt.Scale(scheme=COLOR_SCHEME)),
                    opacity=alt.value(0.5),
                    tooltip=["Action:O", alt.Tooltip("Iteration:Q", format=","),
                             alt.Tooltip("Action Count:Q", format=",")]
                ).properties(
                    width=200,
                    height=200
                ).facet(
                    column=alt.Column("Policy:O", title="Policy",
                                      header=alt.Header(orient="bottom")),
                    title=title
                )
                st.altair_chart(chart2)
                bar.progress((5 * i + 3) / 20, text=f"Rendering charts. Please wait... ({5 * i + 3} / 20)")
            with tabs[2]:
                st.dataframe(summary_long)
                bar.progress((5 * i + 4) / 20, text=f"Rendering data. Please wait... ({5 * i + 4} / 20)")
        bar.empty()

if __name__ == '__main__':
    iteration_level_analysis()
