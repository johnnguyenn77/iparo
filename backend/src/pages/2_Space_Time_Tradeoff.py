from typing import Literal

import streamlit as st
import altair as alt

from components.utils import *


def spacetime_tradeoff():
    error_message = st.empty()

    policy_group = st.selectbox(POLICY_GROUPS, "Choose your Linking Policy Group")

    aggregate_names = {"min": "Minimum", "q1": "1st Quartile", "median": "Median",
                       "q3": "3rd Quartile", "max": "Maximum", "mean": "Mean"}
    with st.form('form'):
        # Pass 1: Get all names of files
        policy_group.display()
        scale = st.selectbox("Select Scale", SCALES)
        statistic = st.selectbox("Choose Aggregation Function for IPFS Retrieval",
                                 ["mean", "min", "q1", "median", "q3", "max"], format_func=lambda x: aggregate_names[x])
        log_scale = st.checkbox("Logarithmic Scale", help="Enables both the x-axis and y-axis to be displayed with "
                                                          "a symmetric logarithmic scale.")
        submitted = st.form_submit_button()

    if submitted:
        listed_policies = policy_group.get_value()
        if not listed_policies or not version_densities:
            error_message.error("You must select at least one linking policy and one version density to view.")
        # else:
        #     scales = [scale]
        #     nth_retrieval_df = get_summary_data(listed_policies, version_densities, "Time", scales)
        #     time_retrieval_df = get_summary_data(listed_policies, version_densities, "Nth", scales)
        #     store_df = get_summary_data(listed_policies, version_densities, "Store", scales,
        #                                 col_index=BasicOpType.LINKS)
        #     st.header("Output")
        #     nth_retrieval_df = rename_nonindex_columns(nth_retrieval_df, " (Nth)")
        #     time_retrieval_df = rename_nonindex_columns(time_retrieval_df, " (Time)")
        #     store_df = rename_nonindex_columns(store_df, " (Store)")
        #     tab1, tab2, tab3, tab4 = st.tabs(["Scatterplot Results 📈", "Scatterplot Data 🔢",
        #                                       "Ranked Results 🏆", "Ranking Data 🔢"])
        #     scale_type: Literal['symlog', 'identity'] = "symlog" if log_scale else "identity"
        #     store_retrieve_df = store_df.join([drop_index_cols(time_retrieval_df), drop_index_cols(nth_retrieval_df)])
        #
        #     with tab1:
        #         chart = alt.Chart(store_retrieve_df,
        #                           title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval Performance (Time) - "
        #                                                 f"{aggregate_names[statistic]}", align='center',
        #                           anchor="middle", fontSize=20)).mark_point().encode(
        #             x=alt.X(f"mean (Store):Q", title="Mean IPFS Links Per Node").scale(type=scale_type),
        #             y=alt.Y(f"{statistic} (Time):Q", title="IPFS Retrieve (Time)").scale(type=scale_type),
        #             color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
        #                             scale=alt.Scale(scheme=COLOR_SCHEME)),
        #             shape=alt.Shape("Density:O", legend=alt.Legend(labelLimit=400))
        #         )
        #         st.altair_chart(chart)
        #         chart2 = alt.Chart(store_retrieve_df,
        #                            title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval Performance (Nth) - "
        #                                                  f"{aggregate_names[statistic]}", align='center',
        #                                                  anchor="middle", fontSize=20)).mark_point().encode(
        #             x=alt.X(f"mean (Store):Q", title="Mean IPFS Links Per Node").scale(type=scale_type),
        #             y=alt.Y(f"{statistic} (Nth):Q", title="IPFS Retrieve (Nth)").scale(type=scale_type),
        #             color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
        #                             scale=alt.Scale(scheme=COLOR_SCHEME)),
        #             shape=alt.Shape("Density:O", legend=alt.Legend(labelLimit=400)),
        #         )
        #         st.altair_chart(chart2)
        #     with tab2:
        #         st.dataframe(drop_index_cols(store_retrieve_df))
        #     with tab3:
        #         st.text("The space-time tradeoff is calculated using the product of the retrieval cost "
        #                 "(in IPFS link traversals) and the mean amount of storage space.")
        #
        #         ranked_df_time = store_retrieve_df.copy()
        #         ranked_df_time['Tradeoff'] = ranked_df_time.apply(lambda x: x[f'mean (Store)'] *
        #                                                                     x[f'{statistic} (Time)'],
        #                                                           axis=1)
        #         ranked_df_time.sort_values('Tradeoff', inplace=True)
        #         if len(listed_policies) > 1:
        #             chart3 = alt.Chart(ranked_df_time,
        #                                title=alt.TitleParams(f"Linking Strategy vs. IPFS Retrieval Tradeoff (Time) - "
        #                                                      f"{aggregate_names[statistic]}",
        #                                                      align='center', anchor="middle", fontSize=20)
        #                                ).mark_bar().encode(
        #                 x=alt.X("Policy:N", sort=alt.EncodingSortField(field='Tradeoff',
        #                                                                op='sum',
        #                                                                order='ascending')),
        #
        #                 y=alt.Y("Tradeoff:Q").scale(type=scale_type),
        #                 color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
        #                                 scale=alt.Scale(scheme=COLOR_SCHEME)),
        #                 column=alt.Column("Density:O")
        #             ).resolve_scale(x='independent').configure_axisX(labelLimit=400)
        #         else:
        #             chart3 = alt.Chart(ranked_df_time,
        #                                title=alt.TitleParams(f"{listed_policies[0]}: IPFS Retrieval Tradeoff (Time) - "
        #                                                      f"{aggregate_names[statistic]}", align='center',
        #                                                      anchor="middle", fontSize=20)
        #                                ).mark_bar().encode(
        #                 x=alt.X("Density:N", sort=alt.EncodingSortField(field='Tradeoff',
        #                                                                 op='sum',
        #                                                                 order='ascending')),
        #
        #                 y=alt.Y("Tradeoff:Q").scale(type=scale_type),
        #                 color=alt.Color("Density:O", legend=alt.Legend(labelLimit=400),
        #                                 scale=alt.Scale(scheme=COLOR_SCHEME)))
        #         st.altair_chart(chart3)
        #
        #         ranked_df_time = store_retrieve_df.copy()
        #         ranked_df_time['Tradeoff'] = ranked_df_time.apply(lambda x: x[f'mean (Store)'] *
        #                                                                     x[f'{statistic} (Time)'],
        #                                                           axis=1)
        #         ranked_df_time.sort_values('Tradeoff', inplace=True)
        #
        #         ranked_df_seq_num = store_retrieve_df.copy()
        #         ranked_df_seq_num['Tradeoff'] = store_retrieve_df.apply(
        #             lambda x: x[f'mean (Store)'] * x[f'{statistic} (Nth)'], axis=1)
        #         ranked_df_seq_num.sort_values('Tradeoff', inplace=True)
        #         if len(listed_policies) > 1:
        #             chart4 = alt.Chart(ranked_df_seq_num,
        #                                title=alt.TitleParams(f"Linking Strategy vs. IPFS Retrieval Tradeoff (Sequence "
        #                                                      f"Number) - {aggregate_names[statistic]}",
        #                                                      align='center', anchor="middle", fontSize=20)
        #                                ).mark_bar().encode(
        #                 x=alt.X("Policy:N", sort=alt.EncodingSortField(field='Tradeoff',
        #                                                                op='sum',
        #                                                                order='ascending')),
        #
        #                 y=alt.Y("Tradeoff:Q").scale(type=scale_type),
        #                 color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
        #                                 scale=alt.Scale(scheme=COLOR_SCHEME)),
        #                 column=alt.Column("Density:O")
        #             ).resolve_scale(x='independent').configure_axisX(labelLimit=400)
        #         else:
        #             chart4 = alt.Chart(ranked_df_time,
        #                                title=alt.TitleParams(f"{listed_policies[0]}: IPFS Retrieval Tradeoff "
        #                                                      f"(Sequence Number) - {aggregate_names[statistic]}",
        #                                                      align='center', anchor="middle", fontSize=20)
        #                                ).mark_bar().encode(
        #                 x=alt.X("Density:N", sort=alt.EncodingSortField(field='Tradeoff',
        #                                                                 op='sum',
        #                                                                 order='ascending')),
        #
        #                 y=alt.Y("Tradeoff:Q").scale(type=scale_type),
        #                 color=alt.Color("Density:O", legend=alt.Legend(labelLimit=400),
        #                                 scale=alt.Scale(scheme=COLOR_SCHEME)))
        #         st.altair_chart(chart4)
        #     with tab4:
        #         st.subheader("Retrieval by Time Tradeoff")
        #         ranked_df_time = rank_and_sort_tradeoff(ranked_df_time)
        #         ranked_df_time_display = ranked_df_time[['Policy', 'Density', f'{statistic} (Store)',
        #                                                  f'{statistic} (Time)', 'Tradeoff', 'Rank']].rename(
        #             columns={f'{statistic} (Store)': f'{aggregate_names[statistic]} (Links)',
        #                      f'{statistic} (Time)': f'{aggregate_names[statistic]} (IPFS Retrieve - Time)'})
        #         st.dataframe(ranked_df_time_display)
        #         st.subheader("Retrieval by Sequence Number Tradeoff")
        #         ranked_df_seq_num = rank_and_sort_tradeoff(ranked_df_seq_num)
        #         ranked_df_seq_num_display = ranked_df_seq_num[['Policy', 'Density', f'{statistic} (Store)',
        #                                                        f'{statistic} (Nth)', 'Tradeoff', 'Rank']].rename(
        #             columns={f'{statistic} (Store)': f'{aggregate_names[statistic]} (Links)',
        #                      f'{statistic} (Nth)': f'{aggregate_names[statistic]} (IPFS Retrieve - Nth)'})
        #         st.dataframe(ranked_df_seq_num_display)


if __name__ == '__main__':
    spacetime_tradeoff()
