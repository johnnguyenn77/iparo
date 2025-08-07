import streamlit as st
from streamlit import session_state as ss
import altair as alt

from components.CheckboxGroup import CheckboxGroup
from components.utils import *


def display_chart(df_ranked: pd.DataFrame, n_policies_selected: int, title: str,
                  formatted_statistic: Literal['mean', 'max', 'median'] = 'mean',
                  scale_type: Literal['symlog', 'identity'] = 'identity'):
    chart = alt.Chart(df_ranked).mark_bar().encode(
        y=alt.Y("Tradeoff:Q").scale(type=scale_type),
        color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                        scale=alt.Scale(scheme=COLOR_SCHEME))
    )

    if n_policies_selected > 1:
        rankings_chart = (chart.encode(x=alt.X("Policy:O",
                                               sort=alt.EncodingSortField(field='Tradeoff',
                                                                          order='ascending')),
                                       column=alt.Column("Density:O")
                                       ).resolve_scale(x='independent')
                          .configure_axisX(labelLimit=400)
                          .properties(title=alt.TitleParams(f"Policy Environment vs. Tradeoff ({title})"
                                                            f" - {formatted_statistic}",
                                                            align='center', anchor="middle", fontSize=20)))
        st.altair_chart(rankings_chart)
    elif n_policies_selected == 1:
        chart = (chart.encode(x=alt.X("Density:O",
                                      sort=alt.EncodingSortField(field='Tradeoff',
                                                                 order='ascending')),
                              ).configure_axisX(labelLimit=400)
                 .properties(title=alt.TitleParams(f"{df_ranked.iloc[0].Policy} - Tradeoff ({formatted_statistic})",
                                                   align='center', anchor="middle", fontSize=20)))

        st.altair_chart(chart)
    else:
        st.error("Expected at least one policy selected, got none.")


def spacetime_tradeoff():
    if 'selected_policies' not in st.session_state:
        st.switch_page('pages/2_Select_Policies.py')

    with st.form('environment_form'):
        st.header("Select Environment")
        statistic: Literal['mean', 'median', 'max'] = st.selectbox("Select Aggregation Function",
                                                                   ['mean', 'median', 'max'], format_func=capitalize)
        scale: int = st.selectbox("Select Scale", SCALES)
        log_scale = st.checkbox("Logarithmic Scale", help="Displays the graphs with a symmetric log-scale x-axis and "
                                                          "y-axis.")
        submitted = st.form_submit_button()

    if submitted:
        try:
            policies_selected = ss['selected_policies']
            n_policies_selected = len(ss['policy_names'])
            formatted_statistic = capitalize(statistic)
            scale_type: Literal['identity', 'symlog'] = 'symlog' if log_scale else 'identity'
            df1 = get_summary_data(policies_selected, DENSITIES, 'Store', [scale],
                                   [Action.LINKS], agg_func=statistic)
            df1.name = "IPFS Links Per Node"
            df2 = get_summary_data(policies_selected, DENSITIES, 'Nth', [scale],
                                   [Action.IPFS_RETRIEVE], agg_func=statistic)
            df2.name = "IPFS Retrieves (Nth)"
            df3 = get_summary_data(policies_selected, DENSITIES, 'Time', [scale],
                                   [Action.IPFS_RETRIEVE], agg_func=statistic)
            df3.name = "IPFS Retrieves (Time)"
            df_combined = pd.concat([df1, df2, df3], axis=1)
            df = df_combined.reset_index()
            df_long = (df.drop(columns='Scale').melt(['Group', 'Param', 'Density', 'IPFS Links Per Node']))
            df_long.loc[df_long.Param == 'None', 'Policy'] = df_long.Group
            df_long.loc[df_long.Param != 'None', 'Policy'] = df_long.Group + " - " + df_long.Param
            df_long = (df_long.assign(Environment=lambda x: x.Density + " - " + x.variable)
                       .drop(columns=["Group", "Param"]))
            st.header("Output")
            st.subheader("Space-Time Tradeoff")
            tabs = st.tabs(["Scatterplot Results 📈", "Scatterplot Data 🔢"])
            with tabs[0]:
                chart = alt.Chart(df_long, title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval "
                                                                 f"Performance - {formatted_statistic}",
                                                                 align='center', anchor="middle",
                                                                 fontSize=20)).mark_point().encode(
                    x=alt.X("IPFS Links Per Node:Q", title="IPFS Links Per Node").scale(type=scale_type),
                    color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                                    scale=alt.Scale(scheme=COLOR_SCHEME)),
                    shape=alt.Shape("Environment:O", legend=alt.Legend(labelLimit=400)),
                    y=alt.Y("value:Q", title="IPFS Retrieve Operations").scale(type=scale_type),
                    opacity=alt.value(0.5)).properties(width=600, height=300 + 20 * len(policies_selected))
                st.altair_chart(chart)
            with tabs[1]:
                st.dataframe(df_combined)

            st.subheader("Space-Time Tradeoff Rankings")
            st.text("The space-time tradeoff is calculated using the product of the retrieval cost "
                    "(in IPFS link traversals) and the mean amount of storage space.")
            st.markdown("#### Time Retrievals")
            tabs_ranked_time = st.tabs(["Ranked Results 🏆", "Ranking Data 🔢"])
            df_ranked = df_long.assign(Tradeoff=lambda x: x['IPFS Links Per Node'] * x.value
                                       ).sort_values('Tradeoff')
            with tabs_ranked_time[0]:
                df_ranked_time: pd.DataFrame = df_ranked.loc[df_ranked.variable == "IPFS Retrieves (Time)"]
                display_chart(df_ranked_time, n_policies_selected,
                              "Time Retrieval", formatted_statistic, scale_type)
            with tabs_ranked_time[1]:
                display_df_time = rank_and_sort_tradeoff(df_ranked_time)
                display_df_time = display_df_time.drop(columns=["Environment", "variable"]
                                                       ).rename(columns={"value": "IPFS Retrieves (Nth)"}
                                                                ).set_index(["Policy", "Density"])
                st.dataframe(display_df_time)
            st.markdown("#### Nth Retrievals")
            tabs_ranked_nth = st.tabs(["Ranked Results 🏆", "Ranking Data 🔢"])
            with tabs_ranked_nth[0]:
                df_ranked_nth: pd.DataFrame = df_ranked.loc[df_ranked.variable == "IPFS Retrieves (Nth)"]
                display_chart(df_ranked_nth, n_policies_selected,
                              "Nth Retrieval", formatted_statistic, scale_type)
            with tabs_ranked_nth[1]:
                display_df_nth = rank_and_sort_tradeoff(df_ranked_nth)
                display_df_nth = display_df_nth.drop(columns=["Environment", "variable"]
                                                     ).rename(columns={"value": "IPFS Retrieves (Nth)"}
                                                              ).set_index(["Policy", "Density"])
                st.dataframe(display_df_nth)
        except UnboundLocalError:  # Ignored
            pass


if __name__ == '__main__':
    spacetime_tradeoff()
