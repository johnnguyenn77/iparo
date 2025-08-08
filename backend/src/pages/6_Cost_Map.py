from typing import Literal

import altair as alt
import pandas as pd
import streamlit as st
from streamlit import session_state as ss

from components.utils import *


def cost_map():
    if 'selected_policies' not in ss:
        st.switch_page("pages/2_Select_Policies.py")
    st.title("Cost Map")
    with st.form('form'):
        st.header("Choose Environment")
        statistic: Literal['mean', 'median', 'max'] = st.selectbox("Select Aggregation Function",
                                                                   ['mean', 'median', 'max'], format_func=capitalize)
        scale: int = st.selectbox("Select Scale", SCALES)
        st.markdown("#### Graph Display Options")
        log_scale = st.checkbox("Logarithmic Scale", help="Displays the graphs with a symmetric log-scale x-axis and "
                                                          "y-axis.")
        submitted = st.form_submit_button()
    if submitted:
        st.header("Memory Requirements")
        formatted_statistic = capitalize(statistic)
        scale_type: Literal['symlog', 'identity'] = "symlog" if log_scale else 'identity'
        summary: pd.Series = get_summary_data(ss['selected_policies'], DENSITIES, "Store", [scale],
                                              [Action.LINKS], statistic
                                              )
        summary_df = summary.reset_index().rename(columns={statistic: formatted_statistic})
        memory_max = summary_df[formatted_statistic].max()
        memory_min = summary_df[formatted_statistic].min()
        if log_scale:
                proportion_col = (np.log((1 + summary_df[formatted_statistic]) / (1 + memory_min))
                                  / np.log((1 + memory_max) / (1 + memory_min) + 1e-10))
        else:
            proportion_col = summary_df[formatted_statistic] / memory_max
        helper_df1 = summary_df.assign(Proportion=proportion_col)

        title = alt.TitleParams("Mean Storage Link Count", align='center', anchor="middle", fontSize=20)
        base_chart_memory = alt.Chart(helper_df1, title=title).mark_rect().encode(
            x='Density:O',
            y='Policy:O',
            color=alt.Color(f"{formatted_statistic}:Q", scale=alt.Scale(scheme="viridis",
                                                                        domainMin=min(memory_max, max(1, memory_min)),
                                                                        domainMax=max(1, memory_max),
                                                                        type=scale_type), sort='descending')
        )

        heatmap_memory = (base_chart_memory + base_chart_memory.mark_text().encode(
            text=alt.Text(f'{formatted_statistic}:Q', format=",.3"),
            color=(alt.when(alt.datum.Proportion < 0.5)
                   .then(alt.value('black')).otherwise(alt.value('white'))),
            size=alt.value(16),
        )).configure_axisY(labelLimit=400)
        tabs = st.tabs(["Heatmap", "Data"])
        with tabs[0]:
            st.altair_chart(heatmap_memory)
        with tabs[1]:
            st.dataframe(summary_df)
        st.header("Time Requirements")
        tabs = st.tabs(["Heatmap", "Data"])
        with tabs[0]:
            summary: pd.DataFrame = pd.concat([get_summary_data(ss['selected_policies'], DENSITIES, op, [scale],
                                                                RETRIEVE_ACTION_LIST.copy(), statistic
                                                                ).reset_index().assign(Operation=op) for op in
                                               OP_TYPES])
            summary_df = summary.reset_index().drop(columns=["Scale", "index"]
                                                    ).rename(columns={statistic: formatted_statistic})
            time_max = summary_df[formatted_statistic].max()
            time_min = summary_df[formatted_statistic].min()
            if log_scale:
                proportion_col = (np.log((1 + summary_df[formatted_statistic]) / (1 + time_min))
                                  / np.log((1 + time_max) / (1 + time_min) + 1e-10))
            else:
                proportion_col = summary_df[formatted_statistic] / time_max

            helper_df = summary_df.assign(Proportion=proportion_col)
            base_chart = alt.Chart(helper_df).mark_rect().encode(
                x='Action:O',
                y='Density:O',
                color=alt.Color(f"{formatted_statistic}:Q", scale=alt.Scale(scheme="viridis",
                                                                            domainMin=time_min,
                                                                            domainMax=max(1, time_max),
                                                                            type=scale_type), sort='descending')
            )
            title = alt.TitleParams("Number of Actions", align='center', anchor="middle", fontSize=20)
            heatmap = (base_chart + base_chart.mark_text().encode(
                text=alt.Text(f'{formatted_statistic}:Q', format=",.3"),
                color=(alt.when(alt.datum.Proportion < 0.5)
                       .then(alt.value('black')).otherwise(alt.value('white'))),
                size=alt.value(16),
            )).properties(width=200, height=100).facet(row='Policy:O', column='Operation:O', title=title
                                                       ).configure_axisY(labelLimit=400)
            st.altair_chart(heatmap)
        with tabs[1]:
            summary_df = pd.pivot_table(summary_df, columns=['Operation', 'Action'], index=['Policy', 'Density'])
            st.dataframe(summary_df)


if __name__ == '__main__':
    cost_map()
