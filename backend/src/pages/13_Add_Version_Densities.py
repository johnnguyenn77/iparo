from components.VersionDensityEditor import VersionDensityEditor
import streamlit as st
from streamlit import session_state as ss


def get_version_density(density_args: list[str]):
    if 'density_key' not in ss:
        st.error("Please provide a version density key.")
    if 'densities' not in ss:
        ss['densities'] = {}
    density_key = ss['density_key']
    n = len(ss['densities'])
    ss['densities'][density_key] = (" ".join(density_args))
    if len(ss['densities']) == n:  # Duplicate error message
        st.error("Failed to add version density because it is a duplicate. Please try again.")
    else:
        ss['success_message'] = f"Successfully added version density: {density_key}"
        st.switch_page("pages/12_View_Environments.py")


def add_version_densities():
    editor = VersionDensityEditor(get_version_density)
    editor.display()


if __name__ == '__main__':
    add_version_densities()
