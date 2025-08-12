import streamlit as st
from streamlit import session_state as ss

from components.utils import DENSITIES, SCALES


def general_settings():
    st.title("General Settings")
    st.text("You must fill in the general settings before selecting policies and accessing reports.")
    with st.form("form"):
        st.header("Filter Settings")
        st.subheader("Version Density Settings")
        density = st.selectbox("Density", DENSITIES, help="Version density to be displayed.")
        st.subheader("Version Volume Settings")
        scale = st.selectbox("Version Volume", SCALES, help="The chain length (in number of IPAROs), to "
                                                            "be used for the Cost Map")

        st.subheader("Graph Display Settings")
        log_scale = st.checkbox("Logarithmic Scale", help="Use logarithmic scale on both the X-axis and "
                                                          "Y-axis for line charts, and color for heatmaps.")
        submitted = st.form_submit_button()

    if submitted:
        ss['density'] = density
        ss['scale'] = scale
        ss['log_scale'] = log_scale
        st.switch_page("pages/3_Select_Policies.py")


if __name__ == '__main__':
    general_settings()
