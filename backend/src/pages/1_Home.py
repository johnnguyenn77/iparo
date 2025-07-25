import streamlit as st

if __name__ == '__main__':
    st.set_page_config(page_title="Home")
    st.title("Home")
    st.text("The IPARO Simulation App lets users compare different linking strategies "
            "to see the number of operations under different testing environments and "
            "different scales. The terminology will be captured below:")
    st.markdown("""
    - **Big Head Long Tail (BHLT)**: A version density whose time distribution is defined by a big head
    (meaning that a significant chunk of IPAROs will have a time on one side) and a long tail (meaning 
    that the median time for the IPAROs in the IPFS is far from the mode).
    - **Density**: A version density represents the distribution with respect to the time.
    - **Policy**: A way to store the links along with the IPAROs. Minimizing the links and the
    number of retrievals required is important to maintaining a fast and reliable database
    in the IPFS. We may use the term "policy" and "strategy" interchangeably.
    - **Scale**: The scale defines the number of nodes in the IPFS. We may use the term "scale" and "volume" 
    interchangeably. There are five scales: Single has 1 node, Small has 10 nodes, Medium has 100 nodes,
    Large has 1000 nodes, and Hyperlarge has 10000 nodes.
    - **Space-Time Tradeoff**: A phenomenon where the amount of storage space required,
    represented by the number of links stored in the IPFS at the given scale, is balanced
    with the number of link traversals required to retrieve an IPARO object in the IPFS
    with a uniformly distributed time or sequence number.
    """)

