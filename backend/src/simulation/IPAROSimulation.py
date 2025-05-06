import streamlit as st
import pandas as pd
import altair as alt

st.title("IPARO Simulation")


df_store = pd.read_csv("../../results/results_store.csv", delimiter="\t")
df_retrieve = pd.read_csv("../../results/results_retrieve.csv", delimiter="\t")

with st.expander("About this app"):
    st.text("This app lets the user compare linking strategies in the simulation under different testing environments.")

# List all strategies
with st.form('form'):
    strategies = st.multiselect('Linking Strategy', df_retrieve.strategy.unique())
    density = st.selectbox('Density', df_retrieve.density.unique())
    op_type = st.selectbox('Type of Operation', ['Store Link Counts', 'Store Operation Counts', 'Retrieve Number', 'Retrieve Date'])
    logscale = st.checkbox('Logarithmic Scale')

    submitted = st.form_submit_button('Submit')


if submitted:
    def filter_relevant_data(data: pd.DataFrame):
        return data[(data.density == density) & data.strategy.isin(strategies)]

    def process_relevant_data(data: pd.DataFrame):
        return (data.rename(columns={'ipfs_retrieve_count': 'IPFS Retrieve Count'})
                .groupby(['strategy', 'volume']).describe())

    st.header("Results")

    if op_type.startswith('Store'):
        data = filter_relevant_data(df_store)
    elif op_type == 'Retrieve Number':
        data = filter_relevant_data(df_retrieve.loc[df_retrieve.type == 'number'])
        relevant_data = process_relevant_data(data)
        st.write(relevant_data)
    else:
        data = filter_relevant_data(df_retrieve.loc[df_retrieve.type == 'date'])
        relevant_data = process_relevant_data(data)
        st.write(relevant_data)

    if not op_type.startswith('Store'):
        title = alt.TitleParams('Linking Strategy Performance - ' + op_type, anchor='middle')
        chart = alt.Chart(data, title=title).mark_boxplot(ticks=True).encode(
            x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
            y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(type='log' if logscale else 'linear'),
            color="strategy:O",
            column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000], header=alt.Header(orient="bottom"))
        ).properties(
            width=100
        ).configure_facet(
            spacing=0
        ).configure_view(
            stroke=None
        )

    else:
        if op_type == 'Store Link Counts':
            title = alt.TitleParams('IPFS Storage Performance', anchor='middle')
            st.write(data)
            chart = alt.Chart(data, title=title).mark_line().encode(
                x=alt.X('volume:Q', title="Version Volume"),
                y=alt.Y('num_links:Q', title="Number of Links").scale(type='log' if logscale else 'linear'),
                color='strategy:N',
            )
        else:
            st.write(data)
            relevant_data = data.rename(columns={'store_ipfs_retrieve': 'IPFS Retrieve Count',
                                                 'store_ipfs_store': 'IPFS Store Count',
                                                 'store_ipns_update': 'IPNS Update Count',
                                                 'store_ipns_get': 'IPNS Get Count'})

            relevant_data = pd.melt(relevant_data, ["strategy", "volume"],
                                    value_vars=['IPNS Update Count', 'IPNS Get Count',
                                                'IPFS Store Count', 'IPFS Retrieve Count'],
                                    value_name="operation_count",
                                    var_name="operation_type")

            title = alt.TitleParams('Operation Counts', anchor='middle')
            chart = alt.Chart(relevant_data, title=title).mark_line().encode(
                x=alt.X('volume:Q', title="Version Volume"),
                y=alt.Y('operation_count:Q', title="Operation Counts")
                .scale(type='log' if logscale else 'linear'),
                color="strategy:O",
                strokeDash="operation_type:O"
            )

    st.write(chart)