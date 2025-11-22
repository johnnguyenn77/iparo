import streamlit as st
from streamlit import session_state as ss

from components.Heatmap import Heatmap
from components.utils import *


def cost_density_map():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    st.title("Cost Map")
    st.header("Storage Requirements")
    scale = ss['scale']
    log_scale = ss['log_scale']
    partial_summaries = []
    for density in DENSITIES:
        partial_summary: pd.Series = get_summary_data(ss['selected_policies'], density, "Store", scale,
                                              [Action.LINKS], 'mean')
        partial_summary_df = pd.DataFrame({"Mean": partial_summary, "Density": partial_summary.map(lambda x: density)})
        partial_summaries.append(partial_summary_df)
    summary = pd.concat(partial_summaries).reset_index()
    map = Heatmap(summary, "Density:O", "Policy:O", "Mean:Q",
                  title="Mean Number of Links Required for Add Node", subtitle=f"Chain Length {scale}",
                  log_scale=log_scale)
    map.display()

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
