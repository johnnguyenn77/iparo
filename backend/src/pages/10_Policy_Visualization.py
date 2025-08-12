import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
from streamlit import session_state as ss

from components.utils import select_policy, select_version_density
from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment
from simulation.IPFS import ipfs
from simulation.LinkingStrategy import LinkingStrategy
from simulation.Operation import StoreOperation, URL
from simulation.VersionDensity import VersionDensity


def policy_visualization():
    if 'policy_group_param' not in ss or 'node_num' not in ss:
        st.switch_page("pages/9_Policy_Visualization_Settings.py")
    ipfs.reset_data()
    policy_group: str = ss['policy_group']
    param: str = ss['policy_group_param']
    node_number: str = ss['node_num']
    policy: LinkingStrategy = select_policy(policy_group, param)
    density: VersionDensity = select_version_density(ss['density'])
    environment: IPAROSimulationEnvironment = IPAROSimulationEnvironment(policy, ss['node_num'], density,
                                                                         [], verbose=True)
    operation = StoreOperation(environment, save_to_file=False)
    operation.execute()

    nx_graph = nx.DiGraph()
    latest_link, _ = ipfs.get_link_to_latest_node(URL)
    first_link = ipfs.retrieve_nth_iparo(0, latest_link)
    positions = {}
    for iparo in ipfs.get_all_iparos(URL):
        curr_num = iparo.seq_num
        nx_graph.add_node(curr_num)
        positions[curr_num] = ((iparo.timestamp - first_link.timestamp) /
                               (latest_link.timestamp - first_link.timestamp), curr_num * 50 * (-1) ** curr_num) \
            if first_link.seq_num != latest_link.seq_num else (0, 0)
        for link in iparo.linked_iparos:
            nx_graph.add_edge(curr_num, link.seq_num)

    st.title("Graph Visualization")
    st.text("X-axis represents the timestamp and Y-axis represents the sequence number.")
    g = nx.draw_networkx(nx_graph, pos=positions, font_color="white")
    with st.container():
        plt.title(f"{str(policy)} - {node_number} nodes")
        st.pyplot(fig=g, clear_figure=True)


if __name__ == '__main__':
    policy_visualization()