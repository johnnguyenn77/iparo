import altair as alt
import pandas as pd
import streamlit as st
from streamlit import session_state as ss

from components.utils import SCALES, get_summary_data, DENSITIES, RETRIEVE_ACTION_LIST, ACTION_LIST, Action, OP_TYPES


def cost_map():
    if 'selected_policies' not in ss:
        st.switch_page("pages/2_Select_Policies.py")
    st.title("Cost Map")
    with st.form('form'):
        st.header("Choose Environment")
        # statistic: Literal['mean', 'median', 'max'] = st.selectbox("Select Aggregation Function",
        #                                                            ['mean', 'median', 'max'], format_func=capitalize)
        scale: int = st.selectbox("Select Scale", SCALES)
        st.markdown("#### Graph Display Options")
        log_scale = st.checkbox("Logarithmic Scale", help="Displays the graphs with a symmetric log-scale x-axis and "
                                                          "y-axis.")
        submitted = st.form_submit_button()
    if submitted:
        st.header("Memory Requirements")
        summary: pd.Series = get_summary_data(ss['selected_policies'], DENSITIES, "Store", [scale],
                                              [Action.LINKS], "mean"
                                              )
        summary_df = summary.reset_index().rename(columns={"mean": "Mean"})
        memory_max = summary_df["Mean"].max()
        helper_df1 = summary_df.assign(Proportion=summary_df["Mean"] / memory_max)

        title = alt.TitleParams("Mean Storage Link Count", align='center', anchor="middle", fontSize=20)
        base_chart_memory = alt.Chart(helper_df1, title=title).mark_rect().encode(
            x='Density:O',
            y='Policy:O',
            color=alt.Color("Mean:Q", scale=alt.Scale(scheme="viridis", domainMin=0), sort='descending')
        )

        heatmap_memory = (base_chart_memory + base_chart_memory.mark_text().encode(
            text=alt.Text('Mean:Q', format=",.3"),
            color=(alt.when(alt.datum.Proportion < 0.5)
                   .then(alt.value('black')).otherwise(alt.value('white'))),
            size=alt.value(16),
        )).configure_axisY(labelLimit=400)
        tabs = st.tabs(["Heatmap", "Data"])
        with tabs[0]:
            st.altair_chart(heatmap_memory)
        with tabs[1]:
            st.dataframe(summary)
        st.header("Time Requirements")
        tabs = st.tabs(["Heatmap", "Data"])
        with tabs[0]:
            summary: pd.Series = get_summary_data(ss['selected_policies'], DENSITIES, OP_TYPES, [scale],
                                                  RETRIEVE_ACTION_LIST.copy(), "mean"
                                                  )
            summary_df = summary.reset_index().rename(columns={"mean": "Mean"}).drop(columns=["Scale"])
            memory_max = summary_df["Mean"].max()
            helper_df = summary_df.assign(Proportion=summary_df["Mean"] / memory_max)

            base_chart = alt.Chart(helper_df).mark_rect().encode(
                x='Action:O',
                y='Density:O',
                color=alt.Color("Mean:Q", scale=alt.Scale(scheme="viridis", domainMin=0), sort='descending')
            )
            heatmap = (base_chart + base_chart.mark_text().encode(
                text=alt.Text('Mean:Q', format=",.3"),
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
