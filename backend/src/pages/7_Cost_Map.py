import altair as alt
import streamlit as st
from streamlit import session_state as ss

from components.Heatmap import Heatmap
from components.utils import *


def cost_map():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    st.title("Cost Map")
    st.header("Memory Requirements")
    scale = ss['scale']
    log_scale = ss['log_scale']
    density = ss['density']

    summary: pd.Series = get_summary_data(ss['selected_policies'], density, "Store", scale,
                                          [Action.LINKS], 'mean')

    summary_df = summary.reset_index().rename(columns={'mean': 'Mean'})

    max_value = summary_df['Mean'].max()
    title = alt.TitleParams("Mean Storage Link Count", subtitle=f"{density} - Chain Length {scale}",
                            subtitleFontSize=16, align='center', anchor="middle", fontSize=20)

    if log_scale:
        n_values_greater = 0
        mantissas = [1, 2, 5]
        power = 0
        y_axis_values = [0]
        while n_values_greater <= 1:
            for mantissa in mantissas:
                value = mantissa * 10 ** power
                if max_value < value:
                    n_values_greater += 1
                if n_values_greater > 1:
                    break
                y_axis_values.append(value)
            else:
                power += 1
        chart_memory = (alt.Chart(summary_df, title=title).mark_bar().encode(
            x=alt.X('Policy:O', sort="y"),
            y=alt.Y('Mean:Q', title="Mean Storage Link Count", subtitle=f"{density} - Chain Length {scale}", scale=alt.Scale(type="symlog"),
                    axis=alt.Axis(values=y_axis_values)),
            color=alt.Color('Policy:O', scale=alt.Scale(scheme=COLOR_SCHEME)))
                        .configure_axisX(labelLimit=400).configure_axisY(labelLimit=400)
                        .configure_legend(labelLimit=400).properties(height=500))
    else:
        chart_memory = (alt.Chart(summary_df, title=title).mark_bar().encode(
            x=alt.X('Policy:O', sort="y"),
            y=alt.Y('Mean:Q', title="Mean Storage Link Count", scale=alt.Scale(type="identity")),
            color=alt.Color('Policy:O', scale=alt.Scale(scheme=COLOR_SCHEME)))
                        .configure_axisX(labelLimit=400).configure_axisY(labelLimit=400)).properties(height=500)

    tabs = st.tabs(["Chart", "Data"])
    with tabs[0]:
        st.altair_chart(chart_memory)
    with tabs[1]:
        st.dataframe(summary_df.rename(columns={"Mean": "Mean Link Count"}), hide_index=True)

    st.header("Time Requirements")
    for op in OP_TYPES:
        st.subheader(OP_NAMES[op])
        summary: pd.DataFrame = get_summary_data(ss['selected_policies'], density, op, [scale],
                                                 RETRIEVE_ACTION_LIST.copy(), 'mean'
                                                 ).reset_index()
        summary_df = summary.reset_index().drop(columns=["index"]
                                                ).rename(columns={'mean': 'Mean'})
        map = Heatmap(summary_df, "Action:O", "Policy:O", "Mean:Q",
                      title=f"Mean Action Counts for {OP_NAMES[op]}", subtitle=f"{density} - Chain Length {scale}",
                      log_scale=log_scale)
        map.display()


if __name__ == '__main__':
    cost_map()
