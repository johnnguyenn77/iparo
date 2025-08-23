import altair as alt
import pandas as pd
from streamlit import session_state as ss

from components.Heatmap import Heatmap
from components.utils import *


def cost_density_map():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    st.title("Cost Map")
    st.header("Memory Requirements")
    scale = ss['scale']
    log_scale = ss['log_scale']
    scale_type: Literal['symlog', 'identity'] = "symlog" if log_scale else 'identity'
    partial_summaries = []
    for density in DENSITIES:
        partial_summary: pd.Series = get_summary_data(ss['selected_policies'], density, "Store", scale,
                                              [Action.LINKS], 'mean')
        partial_summary_df = pd.DataFrame({"mean": partial_summary, "Density": partial_summary.map(lambda x: density)})
        partial_summaries.append(partial_summary_df)
    summary = pd.concat(partial_summaries)
    n_policies = len(ss['policy_names'])
    summary_df = summary.reset_index().rename(columns={'mean': 'Mean'})
    time_max = summary_df['Mean'].max()
    time_min = summary_df['Mean'].min()
    if log_scale:
        proportion_col = (np.log((1 + summary_df['Mean']) / (1 + time_min) + 1e-10)
                          / np.log((1 + time_max) / (1 + time_min) + 1e-10))
    else:
        proportion_col = (summary_df['Mean'] - time_min) / (time_max - max(time_min, 1)) \
            if time_min >= 1 else 0.5

    helper_df = summary_df.assign(Proportion=proportion_col)

    title2 = alt.TitleParams(f"Mean Number of Links Required for Add Node", align='center', anchor="middle",
                            fontSize=20, subtitle=f"Chain Length {ss['scale']}",
                            subtitleFontSize=18)
    base_chart = alt.Chart(helper_df, title=title2).mark_rect().encode(
        x='Density:O',
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

    st.header("Time Requirements")
    for op in OP_TYPES:
        st.subheader(OP_NAMES[op])
        partial_summaries = []
        for density in DENSITIES:
            partial_summary: pd.Series = get_summary_data(ss['selected_policies'], density, op, scale,
                                                          [Action.IPFS_RETRIEVE], 'mean')
            partial_summary_df = pd.DataFrame(
                {"mean": partial_summary, "Density": partial_summary.map(lambda x: density)})
            partial_summaries.append(partial_summary_df)
        summary_df = pd.concat(partial_summaries).reset_index().rename(columns={'mean': 'Mean'})
        map = Heatmap(summary_df, "Density:O", "Policy:O", "Mean:Q",
                      title=f"Mean IPFS Retrieve Counts for {OP_NAMES[op]}", subtitle=f"Chain Length {scale}",
                      log_scale=log_scale)
        map.display()


if __name__ == '__main__':
    cost_density_map()
