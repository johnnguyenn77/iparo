import altair as alt
from streamlit import session_state as ss

from components.Heatmap import Heatmap
from components.utils import *


def cost_calculator():
    if 'density' not in ss:
        st.switch_page("pages/2_General_Settings.py")

    policies = pd.DataFrame([[policy, param] for policy, param in POLICY_GROUP_COMBINATIONS],
                            columns=["Group", "Param"])

    density = ss['density']
    scale = ss['scale']
    df_memory = (pd.DataFrame(get_summary_data(policies, density=density, operation='Store', scales=[scale],
                                               actions=[Action.LINKS], agg_func='mean')).droplevel(['Scale'])
                 .rename(columns={'mean': 'Mean Links Per Node'}))
    st.header("Settings")
    with st.expander('Advanced Settings'):
        st.subheader("Constraints on Memory")
        st.text("Please enter the upper limit on the mean number of links (leave at zero for no limit):")
        memory_limit = st.number_input("Maximum Mean Number of Links")
        st.text("Please enter the upper limit on the amount of time (leave at zero for no limit):")
        time_limit = st.number_input("Time Limit (Microseconds)", min_value=0.0, step=0.01, value=0.0)
        st.subheader("Action Times")
        ipfs_retrieve_time = st.number_input("IPFS Retrieve Time (Nanoseconds)", min_value=0, value=300)
        ipfs_store_time = st.number_input("IPFS Store Time (Nanoseconds)", min_value=0, value=800)
        ipns_get_time = st.number_input("IPNS Get Time (Nanoseconds)", min_value=0, value=1000)
        ipns_update_time = st.number_input("IPNS Update Time (Nanoseconds)", min_value=0, value=1000)
        st.subheader("Retrieve Operation Counts")
        list_all = st.number_input("List All Count", min_value=0, value=10)
        retrieve_first = st.number_input("Retrieve First Operation Count", min_value=0, value=1000)
        retrieve_latest = st.number_input("Retrieve Latest Operation Count", min_value=0, value=1000)
        retrieve_nth = st.number_input("Retrieve By Sequence Number Operation Count", min_value=0, value=1000)
        retrieve_time = st.number_input("Retrieve By Time Operation Count", min_value=0, value=1000)
        exclude_storage_retrieve_costs = st.checkbox("Exclude Storage Retrieve Costs")
        partial_dfs = []
        for op in OP_NAMES:
            partial_df = pd.DataFrame(get_summary_data(policies, operation=op, density=density, scales=[scale],
                                                       actions=RETRIEVE_ACTION_LIST.copy(), agg_func='mean'))
            partial_df = partial_df.assign(Operation=op).reset_index().drop(columns='Scale').rename(
                columns={'mean': 'Mean Time'})
            partial_dfs.append(partial_df)

    st.header("Results")
    data = pd.concat(partial_dfs)
    if not np.isclose(memory_limit, 0, atol=1e-7):
        data_joined = data.join(df_memory, on=['Policy'])
        data = data.where(data_joined['Mean Links Per Node'] < memory_limit)
    table = data.pivot_table(values=['Mean Time'], index=['Policy', 'Operation'], columns=['Action'])

    # Step 1, do product
    # = x^T A y
    st.subheader("Cost Per Operation")
    tabs = st.tabs(['Time Cost Per Operation', 'Time Cost Per Operation Data'])
    with tabs[0]:
        # The columns are sorted by action name
        operation_costs = np.dot(table, np.array([ipfs_retrieve_time, ipfs_store_time, ipns_get_time, ipns_update_time]))
        operation_costs_long = (pd.DataFrame(operation_costs, index=table.index,
                                             columns=['Time Per Operation (Microseconds)']) / 1000).reset_index()
        operation_costs_long['Operation'] = operation_costs_long['Operation'].replace(OP_NAMES_ABBREVIATED)
        operation_costs_table = (operation_costs_long.pivot_table(index=['Policy'], columns=['Operation'],
                                                                  values=['Time Per Operation (Microseconds)']))
        map = Heatmap(operation_costs_long, "Operation:O", "Policy:O", "Time Per Operation (Microseconds):Q",
                      title="Time Cost Per Operation", subtitle=f"{density} - Chain Length {scale}", log_scale=True,
                      show_labels=False)
        map.display()
    with tabs[1]:
        st.dataframe(operation_costs_table)

    st.subheader("Minimize Costs")
    tabs = st.tabs(['Total Time Cost (Ranked)', 'Memory Cost Per Node (Ranked)', 'Cost Data'])
    with tabs[0]:
        time_costs = np.dot(operation_costs_table, np.array([0 if exclude_storage_retrieve_costs else ss['scale'],
                                                             list_all, retrieve_first, retrieve_latest,
                                                             retrieve_nth, retrieve_time])) / 1e6
        time_costs_table = pd.DataFrame(time_costs, index=operation_costs_table.index,
                                        columns=['Total Time Cost (Seconds)'])
        if not np.isclose(time_limit, 0, atol=1e-7):
            time_costs_table = time_costs_table[time_costs_table['Total Time Cost (Seconds)'] < time_limit / 1e6]
        sorted_table = time_costs_table.join(df_memory, how='inner').sort_values(by=['Total Time Cost (Seconds)'])
        ranked_table = sorted_table.head(10)
        excluded = ' - Excluding Store Retrieve Costs' if exclude_storage_retrieve_costs else ''
        title = alt.TitleParams("Time Cost", align='center', anchor="middle",
                                fontSize=20, subtitle=f"Chain Length {str(ss['scale']) + excluded}",
                                subtitleFontSize=18)
        chart = alt.Chart(ranked_table.reset_index(), title=title).mark_bar().encode(
            x=alt.X('Policy:O', sort="y"),
            y='Total Time Cost (Seconds):Q',
            color=alt.Color('Policy:O', scale=alt.Scale(scheme=COLOR_SCHEME))
        ).configure_axisX(labelLimit=400).configure_legend(labelLimit=400).properties(height=600)
        st.altair_chart(chart)
    with tabs[1]:
        sorted_table = sorted_table.sort_values(by=['Mean Links Per Node'])
        ranked_table = sorted_table.head(10)
        title = alt.TitleParams("Memory Cost (Links Per Node)", align='center', anchor="middle",
                                fontSize=20, subtitle=f"Chain Length {ss['scale']}",
                                subtitleFontSize=18)
        chart = alt.Chart(ranked_table.reset_index(), title=title).mark_bar().encode(
            x=alt.X("Policy:O", sort='y'),
            y="Mean Links Per Node:Q",
            color=alt.Color('Policy:O',scale=alt.Scale(scheme=COLOR_SCHEME))
        ).configure_axisX(labelLimit=400).configure_legend(labelLimit=400).properties(height=600)
        st.altair_chart(chart)
    with tabs[2]:
        st.dataframe(sorted_table)


if __name__ == '__main__':
    cost_calculator()
