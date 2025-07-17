import math
import pathlib

import streamlit as st
import pandas as pd
import altair as alt
import os.path

RESULTS_FOLDER = "../Results"


def get_iteration_summary_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Number of rows dedicated to summary is 8 (count, mean, std, min, 25%, 50%, 75%, max).
    summary_stats_labels = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    # Key Assumption: the summary stats labels are located in the bottom of the file.
    # Cutoff is negative from that key assumption.
    cutoff = -len(summary_stats_labels)
    df_iter = df.iloc[:cutoff]
    df_summary = df.iloc[cutoff:]

    return df_iter, df_summary


def policy_name_to_file_name(policy_name: str):
    path = os.path.join(RESULTS_FOLDER, policy_name)
    my_dir = pathlib.Path(path)

    # Assume alphabetical order.
    first_file = next((x for x in my_dir.iterdir() if x.is_file()), None).name
    policy_length = first_file.find("-Hyperlarge")
    # Strip the portion to the right of the filename.
    filename = first_file[:policy_length]
    return filename


op_types = {
    "Get First Node": "First",
    "Get Latest Node": "Latest",
    "List All Nodes": "List",
    "Get Nth Node": "Nth",
    "Get Node at Time T": "Time",
    "Store Nodes": "Store"
}

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("IPARO Simulation App")

    with st.expander("About this app"):
        st.text("This app lets the user compare linking strategies in the simulation under different testing "
                "environments.")

    policies = {}
    policy_names = []
    listed_policies = []
    scales = ["Single", "Small", "Medium", "Large", "Hyperlarge"]

    with st.form('form'):
        st.subheader("Choose your Linking Policies")
        # Pass 1: Get all names of files
        for filename in os.scandir(RESULTS_FOLDER):
            policy_names.append(filename.name)

        cols = st.columns(4)
        n_policies = len(policy_names)
        for i in range(4):
            with cols[i] as col:
                for name in policy_names[i:n_policies:4]:
                    policies[name] = st.checkbox(name)
        scale = st.selectbox("Select Scale", scales)
        submitted = st.form_submit_button()

    # Melt the dataframe. ID by policy, scale, and operation.
    # Scale can be kept in different columns.
    # There are 5 scales, 6 types of operations, and 4 version densities to track.
    # So we want to maybe have tabs for the scale
    # Operations can go in containers
    # There are, in total, 120 different combinations for each strategy.

    if submitted:
        # Handle logic of checking for every strategy.
        densities = ["Uniform", "Linear", "BHLT", "Multipeak"]
        for policy_name in policy_names:
            if policies[policy_name]:
                policy_name_to_file_name(policy_name)
                listed_policies.append(policy_name)

        st.header("Operations")
        # For each operation, do a container. This container will encapsulate one "operation."

        # Setup "Grid" Layout (no supporting functionality sadly, but I can perhaps do a makeshift version.)
        first_col_displayed = ["Uniform", "BHLT"]
        second_col_displayed = ["Linear", "Multipeak"]
        layout = [first_col_displayed, second_col_displayed]
        n_listed_policies = len(listed_policies)
        n_densities = len(densities)
        n_op_types = len(op_types)
        progress_total = (n_densities * n_listed_policies + 4) * n_op_types
        my_bar = st.progress(0.0, text=f"Gathering data. Please wait... (0 / {progress_total})")
        progress = 0
        for i, op in enumerate(op_types):
            ctr = st.container()
            partial_dfs = []
            partial_df_iterations = []
            partial_df_summaries = []

            for j, policy_name in enumerate(listed_policies):
                policy_filename = policy_name_to_file_name(policy_name)
                for k, density in enumerate(densities):
                    my_bar.progress(progress / progress_total,
                                    text=f"Gathering data. Please wait... ({progress} / {progress_total})")
                    filename = f"{RESULTS_FOLDER}/{policy_name}/{policy_filename}-{scale}-{density}-{op_types[op]}.csv"
                    partial_df = pd.read_csv(filename)
                    partial_df_iter, partial_df_summary = get_iteration_summary_split(partial_df)
                    partial_df = partial_df.assign(Policy=policy_name, Density=density)
                    partial_df_iter = partial_df_iter.assign(Policy=policy_name, Density=density)
                    partial_df_summary = partial_df_summary.assign(Policy=policy_name, Density=density)
                    partial_dfs.append(partial_df)
                    partial_df_iterations.append(partial_df_iter)
                    partial_df_summaries.append(partial_df_summary)
                    progress += 1

            my_bar.progress(progress / progress_total,
                            text=f"Rendering charts. Please wait... ({progress} / {progress_total})")
            df = pd.concat(partial_dfs)
            df_iter = pd.concat(partial_df_iterations)
            df_summary = pd.concat(partial_df_summaries)
            with ctr:
                st.subheader(op)
                tab1, tab2, tab3, tab4 = st.tabs(["Results By Strategy 📈", "Results By Iteration 📈",
                                                  "Summary Data 🔢", "Iteration Data 🔢"])
                df_long = pd.melt(df_iter, id_vars=["Policy", "Density", "Iteration"])
                df_long_filtered = {density: df_long[df_long["Density"] == density] for density in densities}
                dfs_filtered = {density: df_iter[df_iter["Density"] == density] for density in densities}
                basic_op_types = ["IPNS Get", "IPNS Update", "IPFS Store", "IPFS Retrieve"]
                if op == 'Store Nodes':
                    basic_op_types.append("Links")
                with tab1:
                    cols = st.columns(2)

                    for col_densities, col in zip(layout, cols):
                        with col:
                            for density in col_densities:
                                title = alt.TitleParams(f'Linking Policy Performance - {op} - {density}',
                                                        anchor='middle')
                                chart = alt.Chart(df_long_filtered[density], title=title
                                                  ).mark_boxplot(ticks=True).encode(
                                    x=alt.X("Policy:O", title=None, axis=alt.Axis(labels=False, ticks=False)),
                                    y=alt.Y("value:Q", title="Operation Count"),
                                    color="Policy:O",
                                    column=alt.Column("variable:N", title="Type of Operation", sort=["IPNS Get",
                                                                                                     "IPNS Update",
                                                                                                     "IPFS Store",
                                                                                                     "IPFS Retrieve"],
                                                      header=alt.Header(orient="bottom"))
                                ).properties(
                                    width=100
                                ).configure_facet(
                                    spacing=0
                                ).configure_view(
                                    stroke=None
                                )
                                col.altair_chart(chart)
                progress += 1
                my_bar.progress(progress / progress_total,
                                text=f"Rendering charts. Please wait... ({progress} / {progress_total})")
                with tab2:
                    tabs2 = st.tabs(basic_op_types)
                    for basic_op, tab in zip(basic_op_types, tabs2):
                        with tab:
                            cols = st.columns(2)
                            for col_densities, col in zip(layout, cols):
                                with col:
                                    for density in col_densities:
                                        title_string = f'Linking Policy Performance - {op} - {density}'
                                        title = alt.TitleParams(title_string, anchor='middle')
                                        chart = alt.Chart(dfs_filtered[density], title=title
                                                          ).mark_line(point=True).encode(
                                            x=alt.X("Iteration:Q", title="Iteration Number"),
                                            y=alt.Y(f"{basic_op}:Q", title=f"{basic_op} Count"),
                                            color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400))
                                        ).properties(
                                            width=100
                                        ).configure_facet(
                                            spacing=0
                                        ).configure_view(
                                            stroke=None
                                        )
                                        col.altair_chart(chart)

                progress += 1
                my_bar.progress(progress / progress_total,
                                text=f"Rendering charts. Please wait... ({progress} / {progress_total})")
                with tab3:
                    df_summary.rename(columns={"Iteration": "Statistic"}, inplace=True)
                    df_summary.set_index(["Policy", "Density", "Statistic"], inplace=True)
                    tab3.dataframe(df_summary)
                progress += 1
                my_bar.progress(progress / progress_total,
                                text=f"Rendering charts. Please wait... ({progress} / {progress_total})")
                with tab4:
                    df_iter.set_index(["Policy", "Density", "Iteration"], inplace=True)
                    tab4.dataframe(df_iter)
                progress += 1
                my_bar.progress(progress / progress_total,
                                text=f"Rendering charts. Please wait... ({progress} / {progress_total})")

            my_bar.progress(progress / progress_total,
                            text=f"Gathering data. Please wait... ({progress} / {progress_total})")
            if progress == progress_total:
                my_bar.empty()
