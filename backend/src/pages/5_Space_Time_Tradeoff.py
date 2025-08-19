import streamlit as st
from streamlit import session_state as ss
import altair as alt

from components.utils import *


def display_chart(df_ranked: pd.DataFrame, n_policies_selected: int, title: str,
                  scale_type: Literal['symlog', 'identity'] = 'identity'):
    density = ss['density']
    chart = (alt.Chart(df_ranked).mark_bar().encode(
        x=alt.X("Policy:O",
                sort=alt.EncodingSortField(field='Tradeoff',
                                           order='ascending')),
        y=alt.Y("Tradeoff:Q").scale(type=scale_type),
        color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                        scale=alt.Scale(scheme=COLOR_SCHEME))
    ).resolve_scale(x='independent').configure_axisX(labelLimit=400)
                          .properties(title=alt.TitleParams(f"Policy vs. Tradeoff ({title}) - Mean - {density}",
                                                            align='center', anchor="middle")))

    if n_policies_selected >= 1:
        st.altair_chart(chart)
    else:
        st.error("Expected at least one policy selected, got none.")


def spacetime_tradeoff():
    if 'selected_policies' not in st.session_state:
        st.switch_page('pages/2_Select_Policies.py')

    st.title("Space-Time Tradeoff")

    try:
        log_scale = ss['log_scale']
        density = ss['density']
        scale = ss['scale']
        policies_selected = ss['selected_policies']
        n_policies_selected = len(ss['policy_names'])
        scale_type: Literal['identity', 'symlog'] = 'symlog' if log_scale else 'identity'
        df1 = get_summary_data(policies_selected, density, 'Store', scale,
                               [Action.LINKS], agg_func='mean')
        df1.name = "IPFS Links Per IPARO"
        df2 = get_summary_data(policies_selected, density, 'Nth', scale,
                               [Action.IPFS_RETRIEVE], agg_func='mean')
        df2.name = "IPFS Retrieves (Nth)"
        df3 = get_summary_data(policies_selected, density, 'Time', scale,
                               [Action.IPFS_RETRIEVE], agg_func='mean')
        df3.name = "IPFS Retrieves (Time)"
        df_combined = pd.concat([df1, df2, df3], axis=1)
        df = df_combined.reset_index()
        df_long = df.melt(['Policy', 'IPFS Links Per IPARO'])
        st.header("Space-Time Tradeoff")
        tabs = st.tabs(["Scatterplot Results 📈", "Scatterplot Data 🔢"])
        with tabs[0]:
            chart = alt.Chart(df_long, title=alt.TitleParams(f"Link Storage vs. IPFS Retrieval "
                                                             f"Performance - Mean",
                                                             align='center', anchor="middle",
                                                             fontSize=20)).mark_point().encode(
                x=alt.X("IPFS Links Per IPARO:Q", title="IPFS Links Per IPARO").scale(type=scale_type),
                color=alt.Color("Policy:O", legend=alt.Legend(labelLimit=400),
                                scale=alt.Scale(scheme=COLOR_SCHEME)),
                y=alt.Y("value:Q", title="IPFS Retrieve Operations").scale(type=scale_type),
                shape="variable:O",
                opacity=alt.value(0.5)).properties(width=600, height=300 + 20 * len(policies_selected))
            st.altair_chart(chart)
        with tabs[1]:
            st.dataframe(df_combined)

        st.header("Space-Time Tradeoff Rankings")
        st.text("The space-time tradeoff is calculated using the product of the retrieval cost "
                "(in IPFS link traversals) and the mean amount of storage space.")
        st.subheader("Retrieval by Time")
        tabs_ranked_time = st.tabs(["Ranked Results 🏆", "Ranking Data 🔢"])
        df_ranked = df_long.assign(Tradeoff=lambda x: x['IPFS Links Per IPARO'] * x.value
                                   ).sort_values('Tradeoff')
        with tabs_ranked_time[0]:
            df_ranked_time: pd.DataFrame = df_ranked.loc[df_ranked.variable == "IPFS Retrieves (Time)"]
            display_chart(df_ranked_time, n_policies_selected,
                          "Retrieval by Time", scale_type)
        with tabs_ranked_time[1]:
            display_df_time = rank_and_sort_tradeoff(df_ranked_time)
            display_df_time = display_df_time.drop(columns=["variable"]
                                                   ).rename(columns={"value": "IPFS Retrieves (Nth)"}
                                                            ).set_index(["Policy"])
            st.dataframe(display_df_time)
        st.subheader("Retrieval by Sequence Number")
        tabs_ranked_nth = st.tabs(["Ranked Results 🏆", "Ranking Data 🔢"])
        with tabs_ranked_nth[0]:
            df_ranked_nth: pd.DataFrame = df_ranked.loc[df_ranked.variable == "IPFS Retrieves (Nth)"]
            display_chart(df_ranked_nth, n_policies_selected,
                          "Sequence Number", scale_type)
        with tabs_ranked_nth[1]:
            display_df_nth = rank_and_sort_tradeoff(df_ranked_nth)
            display_df_nth = display_df_nth.drop(columns=["variable"]
                                                 ).rename(columns={"value": "IPFS Retrieves (Nth)"}
                                                          ).set_index(["Policy"])
            st.dataframe(display_df_nth)
    except UnboundLocalError:  # Ignored
        pass


if __name__ == '__main__':
    spacetime_tradeoff()
