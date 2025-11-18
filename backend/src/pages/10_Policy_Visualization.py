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


def save_chart(chart: alt.Chart):
    try:
        chart.save("chart.png", ppi=300)
        st.success("Chart Successfully Saved")
    except Exception as e:
        st.error(f"Error: {e}")


def save_figure(fig: plt.Figure):
    try:
        fig.savefig("Chart.png", dpi=300)
        st.success("Chart Successfully Saved")
    except Exception as e:
        st.error(f"Error: {e}")


def policy_visualization():
    if 'visualization_density' not in ss or 'node_num' not in ss:
        st.switch_page("pages/9_Policy_Visualization_Settings.py")
    policy: LinkingStrategy = ss['policy']
    node_number: int = ss['node_num']
    density: VersionDensity = ss['visualization_density']
    ipfs.reset_data()
    environment: IPAROSimulationEnvironment = IPAROSimulationEnvironment(policy, ss['node_num'], density, [])
    operation = StoreOperation(environment, save_to_file=False)
    operation.execute()

    nx_graph = nx.DiGraph()
    first_link, latest_link, _ = ipfs.get_links_to_first_and_latest_nodes(URL)
    start_time: int = operation.get_start_time() or first_link.timestamp

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
    absolute_timestamps = {}
    for iparo in ipfs.get_all_iparos(URL):
        curr_num = iparo.seq_num
        nx_graph.add_node(curr_num)
        timestamp = (iparo.timestamp - start_time) / TimeUnit.SECONDS
        absolute_timestamp = (iparo.timestamp - start_time) / (latest_link.timestamp - start_time)
        absolute_timestamps[curr_num] = round(absolute_timestamp * 20) / 20
        for link in iparo.linked_iparos:
            nx_graph.add_edge(curr_num, link.seq_num)
            df.loc[(df['Destination'] == link.seq_num) & (df['Source'] == curr_num), "Linked"] = "Yes"
            df.loc[df['Destination'] == link.seq_num, 'Destination Timestamp'] = \
                (link.timestamp - start_time) / TimeUnit.SECONDS
        df.loc[df['Source'] == curr_num, 'Source Timestamp'] = timestamp
        timestamps[curr_num] = timestamp
    height = 0
    for iparo in ipfs.get_all_iparos(URL):
        seq_num = iparo.seq_num
        index = 0
        curr_num = seq_num - 1
        while curr_num >= 0 and absolute_timestamps[curr_num] == absolute_timestamps[seq_num]:
            index += 1
            curr_num -= 1
        if height < index + 1:
            height = index + 1
        positions[seq_num] = (absolute_timestamps[seq_num], index)
    df = df.assign(Relationship=np.where(np.ravel(xx == yy), "Self", "Linked"))
    df.loc[(df['Linked'] != 'Yes') & (df['Relationship'] != 'Self'), 'Relationship'] = 'None'
    st.title("Graph Visualization")
    max_time = (latest_link.timestamp - start_time) / TimeUnit.SECONDS
    tabs = st.tabs(["Plots", "Graph Image"])

    with tabs[0]:
        st.header("Adjacency Matrix")
        df.loc[df['Relationship'] == 'Self', 'Destination Timestamp'] = df.loc[
            df['Relationship'] == 'Self', 'Source Timestamp']
        chart_seq_num = alt.Chart(df,
                                  title=alt.TitleParams(f'Adjacency Matrix - {policy} - {node_number} Nodes, {density}',
                                                        anchor='middle')
                                  ).mark_rect().encode(
            x=alt.X("Destination:O", title="Destination Node"),
            y=alt.Y("Source:O", title="Source Node"),
            color=alt.Color("Linked:N", scale=alt.Scale(domain=['N/A', "Yes", "No"], range=['gray', 'lime', 'red']))
        )
        st.altair_chart(chart_seq_num)
        st.header("Time Graph")
        st.text("Note that the source and destination timestamps are relative to the absolute minimum, or the first "
                "timestamp in the case of a multipeak distribution.")
        tabs2 = st.tabs(['Graph', 'Data'])
        df_display = df.loc[df['Source'] >= df['Destination']]
        with tabs2[0]:
            st.markdown("**Note**: Saving the chart requires the `vl-convert-python` dependency. To install, "
                        "please use this command:"
                        "```pip install vl-convert-python```")
            chart_time = alt.Chart(df_display
                                   # title=alt.TitleParams(f'Time Plot - {policy} - {node_number} Nodes, {density}',
                                   #                       anchor='middle')
                                   ).mark_circle().encode(
                x=alt.X("Destination Timestamp:Q", title="Destination Timestamp (Seconds)",
                        scale=alt.Scale(domain=[0, max(1000, max_time)])),
                y=alt.Y("Source:O", title="Sequence Number of Source Node"),
                color=alt.Color("Relationship:O", title="Node Relationship",
                                scale=alt.Scale(domain=["Self", "Linked", "None"],
                                                range=["orange", "blue", "gray"]),
                                legend=alt.Legend(orient="top-right")),
                size=alt.value(100),
                opacity=alt.value(0.5),
                tooltip=alt.Tooltip(["Source:Q", "Source Timestamp:Q", "Destination Timestamp:Q"])
            )
            st.altair_chart(chart_time)
            chart_saved = chart_time.properties(width=450, height=200)
            st.button("Save Time Plot", on_click=save_chart, args=(chart_saved,))
        with tabs2[1]:
            st.dataframe(df_display, hide_index=True)

    with tabs[1]:
        st.header("Graph Image")
        fig, ax = plt.subplots()
        nx.draw_networkx_nodes(nx_graph, positions, ax=ax)
        nx.draw_networkx_labels(nx_graph, positions, ax=ax, font_color="white")
        latest_seq_num = node_number - 1
        for i in range(0, latest_seq_num):
            if (latest_seq_num, i) in nx_graph.edges:
                if latest_seq_num == i + 1 or positions[i][1] != positions[latest_seq_num][1]:
                    nx.draw_networkx_edges(nx_graph, positions,
                                           edgelist=[(node_number - 1, i)], ax=ax)
                else:
                    nx.draw_networkx_edges(nx_graph, positions,
                                           edgelist=[(node_number - 1, i)],
                                           connectionstyle=f"""arc3,rad=0.1""", ax=ax)

        plt.suptitle(f"Visualization of {str(policy)}", y=1 + 0.4 / height, fontsize=16)
        plt.title(f"{node_number} Nodes, {density}", fontsize=14)
        fig.set_size_inches(node_number, height)
        st.pyplot(fig=fig, clear_figure=True, use_container_width=False)


if __name__ == '__main__':
    policy_visualization()
