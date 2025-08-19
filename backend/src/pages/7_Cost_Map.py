import altair as alt
from streamlit import session_state as ss

from components.utils import *


def cost_map():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    st.title("Cost Map")
    st.header("Memory Requirements")
    scale = ss['scale']
    log_scale = ss['log_scale']
    density = ss['density']
    scale_type: Literal['symlog', 'identity'] = "symlog" if log_scale else 'identity'
    summary: pd.Series = get_summary_data(ss['selected_policies'], density, "Store", scale,
                                          [Action.LINKS], 'mean')

    n_policies = len(ss['policy_names'])
    summary_df = summary.reset_index().rename(columns={'mean': 'Mean'})

    max_value = summary_df['Mean'].max()
    title = alt.TitleParams("Mean Storage Link Count", align='center', anchor="middle", fontSize=20)

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
            x='Policy:O',
            y=alt.Y('Mean:Q', title="Mean Storage Link Count", scale=alt.Scale(type="symlog"),
                    axis=alt.Axis(values=y_axis_values)),
            color=alt.Color('Policy:O', scale=alt.Scale(scheme=COLOR_SCHEME)))
                        .configure_axisX(labelLimit=400).configure_axisY(labelLimit=400)
                        .configure_legend(labelLimit=400).properties(height=500))
    else:
        chart_memory = (alt.Chart(summary_df, title=title).mark_bar().encode(
            x='Policy:O',
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
        summary_df = summary.reset_index().drop(columns=["Scale", "index"]
                                                ).rename(columns={'mean': 'Mean'})
        time_max = summary_df['Mean'].max()
        time_min = summary_df['Mean'].min()
        if log_scale:
            proportion_col = (np.log((1 + summary_df['Mean']) / (1 + time_min) + 1e-10)
                              / np.log((1 + time_max) / (1 + time_min) + 1e-10))
        else:
            proportion_col = (summary_df['Mean'] - time_min) / (time_max - max(time_min, 1)) \
                if time_min != max(time_min, 1) else 0.5

        helper_df = summary_df.assign(Proportion=proportion_col)
        title = alt.TitleParams(f"Mean Number of Actions for {OP_NAMES[op]}", align='center', anchor="middle",
                                fontSize=20, subtitle=f"{ss['density']} - Chain Length {ss['scale']}",
                                subtitleFontSize=18)
        base_chart = alt.Chart(helper_df, title=title).mark_rect().encode(
            x='Action:O',
            y='Policy:O',
            color=alt.Color("Mean:Q", scale=alt.Scale(scheme="viridis",
                                                      domainMin=time_min,
                                                      domainMax=max(1, time_max),
                                                      type=scale_type), sort='descending'),
        )
        heatmap = (base_chart + base_chart.mark_text().encode(
            text=alt.Text('Mean:Q', format=",.3"),
            color=(alt.when(alt.datum.Proportion < 0.5)
                   .then(alt.value('black')).otherwise(alt.value('white'))),
            size=alt.value(36),
        )).properties(width=400, height=75 * n_policies + 160).configure_axisY(labelLimit=800)
        st.altair_chart(heatmap)


if __name__ == '__main__':
    cost_map()
