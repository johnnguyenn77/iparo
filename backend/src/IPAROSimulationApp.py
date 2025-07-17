import streamlit as st
import pandas as pd
import altair as alt

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("IPARO Simulation App")

    with st.expander("About this app"):
        st.text("This app lets the user compare linking strategies in the simulation under different testing "
                "environments.")

    # List all strategies
    with st.form('form'):
        strategies = st.multiselect('Linking Strategy', df_retrieve.strategy.unique())
        density = st.selectbox('Density', df_retrieve.density.unique())
        logscale = st.checkbox('Logarithmic Scale')
        submitted = st.form_submit_button('Submit')

    if submitted:
        def filter_relevant_data(data: pd.DataFrame):
            return data.loc[(data.density == density) & data.strategy.isin(strategies)]


        def process_relevant_data(data: pd.DataFrame):
            return (data.rename(columns={'ipfs_retrieve_count': 'IPFS Retrieve Count'})
                    .groupby(['strategy', 'volume']).describe())


        ctr1, ctr2, ctr3 = [st.container() for _ in range(3)]

        with ctr1:
            ctr1.header("Retrieve Results")
            data_retrieve = filter_relevant_data(df_retrieve)
            col1, col2 = ctr1.columns(2)
            col1.subheader("Retrieve Number")
            col2.subheader("Retrieve Date")
            with col1:
                tab1, tab2 = st.tabs(["Results 📈", "Data 🔢"])
                with tab1:
                    retrieve_number = data_retrieve.loc[data_retrieve.type == 'date']
                    title = alt.TitleParams('Linking Strategy Performance - Retrieve Number', anchor='middle')
                    chart = alt.Chart(retrieve_number, title=title).mark_boxplot(ticks=True).encode(
                        x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False)),
                        y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(
                            type='log' if logscale else 'linear'),
                        color="strategy:O",
                        column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000],
                                          header=alt.Header(orient="bottom"))
                    ).properties(
                        width=100
                    ).configure_facet(
                        spacing=0
                    ).configure_view(
                        stroke=None
                    )
                    tab1.altair_chart(chart)
                with tab2:
                    tab2.dataframe(process_relevant_data(retrieve_number))
            with col2:
                retrieve_date = data_retrieve.loc[data_retrieve.type == 'number']
                tab1, tab2 = st.tabs(["Results 📈", "Data 🔢"])
                with tab1:
                    title = alt.TitleParams('Linking Strategy Performance - Retrieve Date', anchor='middle')
                    chart = alt.Chart(retrieve_date, title=title).mark_boxplot(ticks=True).encode(
                        x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False)),
                        y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(
                            type='log' if logscale else 'linear'),
                        color="strategy:O",
                        column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000],
                                          header=alt.Header(orient="bottom"))
                    ).properties(
                        width=100
                    ).configure_facet(
                        spacing=0
                    ).configure_view(
                        stroke=None
                    )
                    tab1.altair_chart(chart)
                with tab2:
                    tab2.dataframe(process_relevant_data(retrieve_date))

        # with ctr2:
        #     data_store_opcounts = filter_relevant_data(df_store)
        #     store_ipns_get = data_store_opcounts[["strategy", "volume", "ipns_update"]]
        #     title = alt.TitleParams('IPFS Storage Performance - IPNS Update', anchor='middle')
        #     chart = alt.Chart(store_ipns_get, title=title).encode(
        #         x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
        #         y=alt.Y("ipns_update:Q", title="IPNS Update Count").scale(type='log' if logscale else 'linear'),
        #         color="strategy:O",
        #         column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000],
        #                           header=alt.Header(orient="bottom"))
        #     ).configure_facet(
        #         spacing=0
        #     ).configure_view(
        #         stroke=None
        #     )
        with ctr3:
            ctr3.header("Store Operation Counts")
            data_store_opcounts = filter_relevant_data(df_store_opcounts)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                tab1, tab2 = st.tabs(["IPNS Get Count 📈", "Data 🔢"])
                relevant_data = data_store_opcounts[["strategy", "volume", "ipns_get"]]
                with tab1:
                    title = alt.TitleParams('Storage IPNS Get Count', anchor='middle')
                    chart = alt.Chart(relevant_data, title=title
                                      ).mark_bar().encode(
                        x="volume:N",
                        y=alt.Y("ipns_get:Q", title="IPNS Get Count",
                                scale=alt.Scale(type='log' if logscale else 'linear', domainMin=1, clamp=True))
                    )
                    tab1.altair_chart(chart)
                with tab2:
                    tab2.dataframe(relevant_data)
            with col2:
                tab1, tab2 = st.tabs(["IPNS Update Count 📈", "Data 🔢"])
                relevant_data = data_store_opcounts[["strategy", "volume", "ipns_update"]]
                with tab1:
                    title = alt.TitleParams('Storage IPNS Update Count', anchor='middle')
                    chart = alt.Chart(relevant_data, title=title
                                      ).mark_bar().encode(
                        x="volume:N",
                        y=alt.Y("ipns_update:Q", title="IPNS Update Count",
                                scale=alt.Scale(type='log' if logscale else 'linear', domainMin=1, clamp=True))
                    )
                    tab1.altair_chart(chart)
                with tab2:
                    tab2.dataframe(relevant_data)
            with col3:
                tab1, tab2 = st.tabs(["IPFS Retrieve Count 📈", "Data 🔢"])
                relevant_data = data_store_opcounts[["strategy", "volume", "ipfs_retrieve"]]
                with tab1:
                    title = alt.TitleParams('Storage IPFS Retrieve Count', anchor='middle')
                    chart = alt.Chart(relevant_data, title=title
                                      ).mark_bar().encode(
                        x="volume:N",
                        y=alt.Y("ipfs_retrieve:Q", title="IPFS Retrieve Count",
                                scale=alt.Scale(type='log' if logscale else 'linear', domainMin=1, clamp=True))
                    )
                    tab1.altair_chart(chart)
                with tab2:
                    tab2.dataframe(relevant_data)
            with col4:
                tab1, tab2 = st.tabs(["IPFS Store Count 📈", "Data 🔢"])
                relevant_data = data_store_opcounts[["strategy", "volume", "ipfs_store"]]
                with tab1:
                    title = alt.TitleParams('Storage IPFS Store Count', anchor='middle')
                    chart = alt.Chart(relevant_data, title=title
                                      ).mark_bar().encode(
                        x="volume:N",
                        y=alt.Y("ipfs_store:Q", title="IPFS Store Count",
                                scale=alt.Scale(type='log' if logscale else 'linear', domainMin=1, clamp=True))
                    )
                    tab1.altair_chart(chart)
                with tab2:
                    tab2.dataframe(relevant_data)
            #         title = alt.TitleParams('IPFS Storage Performance - IPNS Update', anchor='middle')
            #         chart = alt.Chart(store_ipns_get, title=title).encode(
            #             x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
            #             y=alt.Y("ipns_update:Q", title="IPNS Update Count").scale(type='log' if logscale else 'linear'),
            #             color="strategy:O",
            #             column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000],
            #                               header=alt.Header(orient="bottom"))
            #         ).configure_facet(
            #             spacing=0
            #         ).configure_view(
            #             stroke=None
            #         )

        # with col1:
        #     row11, row12, row13 = [col1.container() for i in range(3)]
        #     data_retrieve = filter_relevant_data(df_retrieve)
        #     row12.subheader("Retrieve Number")
        #     with row12:
        #         retrieve_number = data_retrieve.loc[data_retrieve.type == 'number']
        #         tab111, tab112 = row12.tabs(["Results 📈", "Data 🔢"])
        #         with tab111:
        #             title = alt.TitleParams('Linking Strategy Performance - Retrieve Number', anchor='middle')
        #             chart = alt.Chart(retrieve_number, title=title).mark_boxplot(ticks=True).encode(
        #                 x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
        #                 y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(type='log' if logscale else 'linear'),
        #                 color="strategy:O",
        #                 column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000], header=alt.Header(orient="bottom"))
        #             )
        #             tab111.altair_chart(chart, use_container_width=True)
        #         with tab112:
        #             tab112.dataframe(process_relevant_data(retrieve_number))
        #
        # with col2:
        #     row21, row22, row23 = [col2.container() for i in range(3)]
        #     row21.subheader("Retrieve Date")
        #     with row21:
        #         tab211, tab212 = row21.tabs(["Retrieve Date Results 📈", "Data 🔢"])
        #         retrieve_date = data_retrieve.loc[data_retrieve.type == 'date']
        #         with tab211:
        #             title = alt.TitleParams('Linking Strategy Performance - Retrieve Date', anchor='middle')
        #             chart = alt.Chart(retrieve_date, title=title).mark_boxplot(ticks=True).encode(
        #                 x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
        #                 y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(type='log' if logscale else 'linear'),
        #                 color="strategy:O",
        #                 column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000], header=alt.Header(orient="bottom"))
        #             ).properties(
        #                 width=500,
        #                 height=300
        #             ).configure_facet(
        #                 spacing=0
        #             ).configure_view(
        #                 stroke=None
        #             )
        #             tab211.altair_chart(chart)
        #             # st.write(chart)
        #         with tab212:
        #             tab212.write(retrieve_date)
        #     with row22:
        #         store_ipns_get = data_store_opcounts[["strategy", "volume", "ipns_update"]]
        #         title = alt.TitleParams('IPFS Storage Performance - IPNS Update', anchor='middle')
        #         chart = alt.Chart(store_ipns_get, title=title).encode(
        #             x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
        #             y=alt.Y("ipns_update:Q", title="IPNS Update Count").scale(type='log' if logscale else 'linear'),
        #             color="strategy:O",
        #             column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000],
        #                               header=alt.Header(orient="bottom"))
        #         ).configure_facet(
        #             spacing=0
        #         ).configure_view(
        #             stroke=None
        #         )
        #
        #         title = alt.TitleParams('IPFS Storage Performance - ' + op_type, anchor='middle')
        #         chart = alt.Chart(data_store, title=title).mark_boxplot(ticks=True).encode(
        #             x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
        #             y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(type='log' if logscale else 'linear'),
        #             color="strategy:O",
        #             column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000], header=alt.Header(orient="bottom"))
        #         ).properties(
        #             width=100
        #         ).configure_facet(
        #             spacing=0
        #         ).configure_view(
        #             stroke=None
        #         )
        #     with tab2:
        #         st.write(data_store)
        # if op_type.startswith('Store'):
        #
        # elif op_type == 'Retrieve Number':
        #     data = filter_relevant_data(df_retrieve.loc[df_retrieve.type == 'number'])
        #     relevant_data = process_relevant_data(data)
        #     st.write(relevant_data)
        # else:
        #     data = filter_relevant_data(df_retrieve.loc[df_retrieve.type == 'date'])
        #     relevant_data = process_relevant_data(data)
        #     st.write(relevant_data)
        #
        # if not op_type.startswith('Store'):
        #     title = alt.TitleParams('Linking Strategy Performance - ' + op_type, anchor='middle')
        #     chart = alt.Chart(data, title=title).mark_boxplot(ticks=True).encode(
        #         x=alt.X("strategy:O", title=None, axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(padding=1)),
        #         y=alt.Y("ipfs_retrieve_count:Q", title="IPFS Retrieve Count").scale(type='log' if logscale else 'linear'),
        #         color="strategy:O",
        #         column=alt.Column("volume:N", title="Version Volume", sort=[10, 100, 1000, 10000], header=alt.Header(orient="bottom"))
        #     ).properties(
        #         width=100
        #     ).configure_facet(
        #         spacing=0
        #     ).configure_view(
        #         stroke=None
        #     )
        #
        # else:
        #     if op_type == 'Store Link Counts':
        #         title = alt.TitleParams('IPFS Storage Performance', anchor='middle')
        #         st.write(data)
        #         chart = alt.Chart(data, title=title).mark_line().encode(
        #             x=alt.X('volume:Q', title="Version Volume"),
        #             y=alt.Y('num_links:Q', title="Number of Links").scale(type='log' if logscale else 'linear'),
        #             color='strategy:N',
        #         )
        #     else:
        #         st.write(data)
        #         relevant_data = data.rename(columns={'store_ipfs_retrieve': 'IPFS Retrieve Count',
        #                                              'store_ipfs_store': 'IPFS Store Count',
        #                                              'store_ipns_update': 'IPNS Update Count',
        #                                              'store_ipns_get': 'IPNS Get Count'})
        #
        #         relevant_data = pd.melt(relevant_data, ["strategy", "volume"],
        #                                 value_vars=['IPNS Update Count', 'IPNS Get Count',
        #                                             'IPFS Store Count', 'IPFS Retrieve Count'],
        #                                 value_name="operation_count",
        #                                 var_name="operation_type")
        #
        #         title = alt.TitleParams('Operation Counts', anchor='middle')
        #         chart = alt.Chart(relevant_data, title=title).mark_line().encode(
        #             x=alt.X('volume:Q', title="Version Volume"),
        #             y=alt.Y('operation_count:Q', title="Operation Counts")
        #             .scale(type='log' if logscale else 'linear'),
        #             color="strategy:O",
        #             strokeDash="operation_type:O"
        #         )
        #
        # st.write(chart)
