from typing import Literal

import altair as alt
import pandas as pd
import streamlit as st
from streamlit import session_state as ss

from components.utils import OP_TYPES, get_summary_data, Action, ACTION_LIST, COLOR_SCHEME


def iteration_level_analysis():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")

    st.title("Iteration-Level Analysis")
    st.markdown("**Warning**: The iteration-level analysis may take longer than the summary-level analysis since up "
                "to 10000 data points may be analyzed as opposed to roughly 8 for summary-level for each operation, "
                "especially for the Store action.")
    bar = st.empty()
    st.header("Results")
    density = ss['density']
    log_scale = ss['log_scale']
    scale = ss['scale']
    scale_type: Literal['identity', 'symlog'] = 'symlog' if log_scale else 'identity'
    for i, op_type in enumerate(OP_TYPES):
        bar.progress(i / 6, text=f"Gathering data. Please wait... ({5 * i} / 30)")
        st.subheader(op_type)
        actions = [action for action in Action if action != Action.LINKS]
        if op_type == 'Store':
            actions.append(Action.LINKS)

        summary: pd.DataFrame = get_summary_data(ss['selected_policies'], density=density,
                                                 scales=scale,
                                                 operation=op_type, actions=actions,
                                                 analyze_all_iterations=True)
        bar.progress((5 * i + 1) / 30, text=f"Rendering charts. Please wait... ({5 * i + 1} / 30)")

        summary_long: pd.DataFrame = summary.melt(id_vars=["Policy", "Density", "Scale", "Iteration"],
                                                  var_name="Action", value_name="Action Count")
        tabs = st.tabs(['Iteration Results By Policy', 'Iteration Results By Action', 'Iteration Data'])
        title = alt.TitleParams(f'Linking Policy Performance - {density} - {op_type}', anchor='middle')
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
            ).resolve_scale(y='independent')
            st.altair_chart(chart1)
            bar.progress((5 * i + 2) / 30, text=f"Rendering charts. Please wait... ({5 * i + 2} / 30)")
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
            ).resolve_scale(y='independent')
            st.altair_chart(chart2)
            bar.progress((5 * i + 3) / 30, text=f"Rendering charts. Please wait... ({5 * i + 3} / 30)")
        with tabs[2]:
            st.dataframe(summary_long)
            bar.progress((5 * i + 4) / 30, text=f"Rendering data. Please wait... ({5 * i + 4} / 30)")
    summary1: pd.DataFrame = get_summary_data(ss['selected_policies'], density=density,
                                              scales=scale,
                                              operation='Store', actions=[Action.IPFS_RETRIEVE],
                                              analyze_all_iterations=True)
    summary2: pd.DataFrame = get_summary_data(ss['selected_policies'], density=density,
                                              scales=scale,
                                              operation='Store', actions=[Action.LINKS],
                                              analyze_all_iterations=True)

    st.header("Individual Chart for Add Node")
    tabs = st.tabs(["Storage Retrieve Costs", "Link Costs"])
    with (tabs[0]):
        chart3 = alt.Chart(summary1, title=alt.TitleParams("IPFS Retrieve Counts for Add Node", align='center',
                                                           anchor="middle", fontSize=20)
                           ).mark_line(point=True, opacity=0.2).encode(
            x=alt.X("Iteration:Q", title="Iteration Number"),
            y=alt.Y(f"IPFS Retrieve:Q", title="Operation Count", scale=alt.Scale(type=scale_type)),
            color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                            scale=alt.Scale(scheme=COLOR_SCHEME)),
            opacity=alt.value(0.5),
            tooltip=["Policy:O", alt.Tooltip("Iteration:Q", format=","),
                     alt.Tooltip("IPFS Retrieve:Q", format=",")]
        )

        st.altair_chart(chart3)
    with tabs[1]:
        chart4 = alt.Chart(summary2, title=alt.TitleParams("Number of Links for Add Node",
                                                           align='center', anchor="middle", fontSize=20)).mark_line(point=True, opacity=0.2).encode(
            x=alt.X("Iteration:Q", title="Iteration Number"),
            y=alt.Y(f"Links:Q", title="Number of Links", scale=alt.Scale(type=scale_type)),
            color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                            scale=alt.Scale(scheme=COLOR_SCHEME)),
            opacity=alt.value(0.5),
            tooltip=["Policy:O", alt.Tooltip("Iteration:Q", format=","),
                     alt.Tooltip("Links:Q", format=",")]
        )

        st.altair_chart(chart4)

    bar.empty()


if __name__ == '__main__':
    iteration_level_analysis()
