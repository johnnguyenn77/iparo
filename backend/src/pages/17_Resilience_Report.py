import altair as alt
import pandas as pd
from streamlit import session_state as ss

from components.utils import *


def resilience_report():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    policies_selected = ss['selected_policies']
    density = ss['density']
    scale = ss['scale']
    if scale > 1000:
        st.error("Data not available for volumes bigger than 1000. Please check back soon.")
    elif scale == 1:
        st.error("There are too few points to analyze for a volume of 1.")
    else:
        partial_dfs = []
        for density in DENSITIES:
            partial_df = get_summary_data(policies_selected, density, 'Unsafe-List',
                                          [scale], UNSAFE_LIST_ALL_ACTIONS.copy(), analyze_all_iterations=True)
            partial_dfs.append(partial_df)
        df = pd.concat(partial_dfs)
        df['Percent Reachable'] = df['Resilience'] * 100
        df['Missing Nodes'] = df['Iteration'] - 1
        with st.expander("Settings"):
            n_points = st.number_input("Number of Points for Moving Average", min_value=1, value=max(1, scale // 10))
            max_x = st.number_input("Maximum Nodes Missing", min_value=0, max_value=scale - 1, value=scale - 1)
        st.header("By Density")
        for name in ss['policy_names']:
            st.subheader(name)
            title = alt.TitleParams("Resilience Chart", align='center', anchor="middle",
                                    fontSize=20, subtitle=f"Chain Length {scale} - {name}",
                                    subtitleFontSize=16)
            data = df[df['Policy'] == shorten_parameter_name(shorten_group_name(name))]
            rolling_average = (data.groupby('Density')['Percent Reachable']
                               .transform(lambda x: x.rolling(n_points, center=True).mean()))
            # data_populated = np.concat((ones, data.loc[:, 'Percent Reachable'], zeros))
            # rolling_average = pd.Series(data_populated).rolling(n_points, center=True).mean().dropna().to_numpy()
            data['Percent Reachable (Moving Average)'] = rolling_average
            df.loc[df['Policy'] == shorten_parameter_name(shorten_group_name(name)),
            'Percent Reachable (Moving Average)'] = rolling_average
            tabs = st.tabs(['Chart', 'Data'])
            with tabs[0]:
                base = alt.Chart(data.loc[data['Missing Nodes'] <= max_x, :]
                                 ).encode(x=alt.X("Missing Nodes:Q",
                                                  scale=alt.Scale(type='linear', domain=[0, max_x])))
                chart = (base.mark_line().encode(
                    y=alt.Y("Percent Reachable (Moving Average):Q",
                            title="Percent Reachable"),
                    color=alt.Color('Density:O', scale=alt.Scale(scheme=COLOR_SCHEME)))
                         + base.mark_circle().encode(
                            y=alt.Y("Percent Reachable:Q"),
                            color=alt.Color('Density:O',
                                            scale=alt.Scale(scheme=COLOR_SCHEME),
                                            legend=alt.Legend(title="Density", symbolOpacity=1, symbolType='stroke')),
                            opacity=alt.value(0.05)
                        )).configure_legend(labelLimit=400
                                            ).properties(title=title, height=400, width=600)
                st.altair_chart(chart)
            with tabs[1]:
                st.dataframe(data[['Missing Nodes', 'Percent Reachable', 'Percent Reachable (Moving Average)']],
                             hide_index=True)
        st.header("All Strategies at Once")
        title = alt.TitleParams("Resilience Chart", align='center', anchor="middle",
                                fontSize=20, subtitle=f"Chain Length {scale} - {density}",
                                subtitleFontSize=16)
        df_density = df.loc[df['Density'] == density]
        tabs = st.tabs(['Chart', 'Data'])
        with tabs[0]:
            base = alt.Chart(df_density.loc[df_density['Missing Nodes'] <= max_x, :]
                             ).encode(x=alt.X("Missing Nodes:Q",
                                              scale=alt.Scale(type='linear', domain=[0, max_x])))
            chart = (base.mark_line().encode(
                y=alt.Y("Percent Reachable (Moving Average):Q",
                        title="Percent Reachable"),
                color=alt.Color('Policy:O', scale=alt.Scale(scheme=COLOR_SCHEME)))
                     + base.mark_circle().encode(
                        y=alt.Y("Percent Reachable:Q"),
                        color=alt.Color('Policy:O',
                                        scale=alt.Scale(scheme=COLOR_SCHEME),
                                        legend=alt.Legend(title="Policy", symbolOpacity=1, symbolType='stroke')),
                        opacity=alt.value(0.05)
                    )).configure_legend(labelLimit=400
                                        ).properties(title=title, height=400, width=600)
            st.altair_chart(chart)
        with tabs[1]:
            st.dataframe(df[['Missing Nodes', 'Percent Reachable', 'Percent Reachable (Moving Average)']],
                         hide_index=True)


if __name__ == '__main__':
    resilience_report()
