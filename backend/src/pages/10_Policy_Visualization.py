import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st
from streamlit import session_state as ss
import altair as alt

from components.utils import select_policy, select_version_density
from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment
from simulation.IPFS import ipfs
from simulation.LinkingStrategy import LinkingStrategy
from simulation.Operation import StoreOperation, URL
from simulation.TimeUnit import TimeUnit
from simulation.VersionDensity import VersionDensity


def policy_visualization():
    if 'policy_group_param' not in ss or 'node_num' not in ss:
        st.switch_page("pages/9_Policy_Visualization_Settings.py")
    ipfs.reset_data()
    policy_group: str = ss['policy_group']
    param: str = ss['policy_group_param']
    node_number: int = ss['node_num']
    policy: LinkingStrategy = select_policy(policy_group, param)
    density: VersionDensity = select_version_density(ss['density'])
    environment: IPAROSimulationEnvironment = IPAROSimulationEnvironment(policy, ss['node_num'], density,
                                                                         [], verbose=True)
    operation = StoreOperation(environment, save_to_file=False)
    operation.execute()

    nx_graph = nx.DiGraph()
    latest_link, _ = ipfs.get_link_to_latest_node(URL)
    first_link = ipfs.retrieve_nth_iparo(0, latest_link)

    srcs = np.arange(node_number)
    dests = np.arange(node_number)
    xs, ys = np.meshgrid(srcs, dests)
    xx = np.ravel(xs)
    yy = np.ravel(ys)
    df = pd.DataFrame({"Source": xx, "Destination": yy,
                       "Source Timestamp": np.zeros_like(xx, dtype=np.float64),
                       "Destination Timestamp": np.zeros_like(xx, dtype=np.float64),
                       "Linked": np.full_like(xx, "N/A", dtype='<U3')})
    df.loc[df['Source'] > df['Destination'], 'Linked'] = "No"
    positions = {}
    timestamps = {}
    edges = []
    relative_timestamps = {}
    for iparo in ipfs.get_all_iparos(URL):
        curr_num = iparo.seq_num
        nx_graph.add_node(curr_num)
        timestamp = (iparo.timestamp - first_link.timestamp) / TimeUnit.SECONDS
        relative_timestamp = (iparo.timestamp - first_link.timestamp) / (latest_link.timestamp - first_link.timestamp)
        relative_timestamps[curr_num] = relative_timestamp
        for link in iparo.linked_iparos:
            nx_graph.add_edge(curr_num, link.seq_num)
            edges.append((curr_num, link.seq_num))
            df.loc[(df['Destination'] == link.seq_num) & (df['Source'] == curr_num), "Linked"] = "Yes"
            df.loc[df['Destination'] == link.seq_num, 'Destination Timestamp'] = \
                (link.timestamp - first_link.timestamp) / TimeUnit.SECONDS
        df.loc[df['Source'] == curr_num, 'Source Timestamp'] = timestamp
        timestamps[curr_num] = timestamp

    for iparo in ipfs.get_all_iparos(URL):
        curr_num = iparo.seq_num
        overlapping_nodes = 0
        for link in iparo.linked_iparos:
            # Get number of overlapping IPAROs
            link_num = link.seq_num
            distance = relative_timestamps[curr_num] - relative_timestamps[link_num]
            if distance < 0.05:  # of the entire timeline
                overlapping_nodes += 1

        positions[curr_num] = (timestamps[curr_num], overlapping_nodes)



    df = df.assign(Relationship=np.where(np.ravel(xx == yy), "Self", "Link"))
    df.loc[(df['Linked'] != 'Yes') & (df['Relationship'] != 'Self'), 'Relationship'] = 'None'
    st.title("Graph Visualization")
    tabs = st.tabs(["Graph Image", "Adjacency Matrix"])
    with tabs[0]:
        st.header("Graph Image")
        fig, ax = plt.subplots()
        nx.draw_networkx_nodes(nx_graph, positions, ax=ax)
        nx.draw_networkx_labels(nx_graph, positions, ax=ax, font_color="white")
        for i in range(0, node_number):
            for j in range(i + 1, node_number):
                if j == i + 1:
                    nx.draw_networkx_edges(nx_graph, positions, edgelist=[(j, i)], ax=ax)
                elif (j, i) in edges:
                    nx.draw_networkx_edges(nx_graph, positions,
                                           edgelist=[(j, i)],
                                           connectionstyle=f"""arc3,rad={0.5 * (timestamps[j] - timestamps[i]) / 
                                                                         (timestamps[node_number - 1] - timestamps[0])}""", ax=ax)
        plt.title(f"{str(policy)} - {node_number} nodes")
        fig.set_size_inches(40, 40)
        st.pyplot(fig=fig, clear_figure=True, use_container_width=False)
    with tabs[1]:
        st.header("Adjacency Matrix")
        df.loc[df['Relationship'] == 'Self', 'Destination Timestamp'] = df.loc[
            df['Relationship'] == 'Self', 'Source Timestamp']
        chart_seq_num = alt.Chart(df,
                                  title=alt.TitleParams(f'Adjacency Matrix - {policy} - {node_number} Nodes, {density}',
                                                        anchor='middle')).mark_rect().encode(
            x=alt.X("Destination:O", title="Destination Node"),
            y=alt.Y("Source:O", title="Source Node"),
            color=alt.Color("Linked:N", scale=alt.Scale(domain=['N/A', "Yes", "No"], range=['gray', 'lime', 'red']))
        )
        st.altair_chart(chart_seq_num)
        st.header("Time Graph")
        st.text("Note that the source and destination timestamps are relative to the first node.")
        tabs2 = st.tabs(['Graph', 'Data'])
        df_display = df.loc[df['Source'] >= df['Destination']]
        with tabs2[0]:
            chart_time = alt.Chart(df_display,
                                   title=alt.TitleParams(f'Time Plot - {policy} - {node_number} Nodes, {density}',
                                                         anchor='middle')
                                   ).mark_circle().encode(
                x=alt.X("Destination Timestamp:Q", title="Destination Timestamp (Seconds)"),
                y=alt.Y("Source Timestamp:Q", title="Source Timestamp (Seconds)"),
                color=alt.Color("Relationship:O",
                                scale=alt.Scale(domain=["Self", "Link", "None"], range=["red", "blue", "gray"])),
                size=alt.value(100),
                opacity=alt.value(0.5)
            )
            st.altair_chart(chart_time)
        with tabs2[1]:
            st.dataframe(df_display, hide_index=True)


if __name__ == '__main__':
    policy_visualization()
