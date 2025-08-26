import altair as alt
import pandas as pd
from streamlit import session_state as ss

from components.utils import *

def resilience_report():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    policies_selected = ss['selected_policies']
    density = ss['density']
    df = get_summary_data(policies_selected, density, 'Unsafe-List',
                          [1000], UNSAFE_LIST_ALL_ACTIONS.copy(), analyze_all_iterations=True)
    df['Resilience'] *= 100
    df['Missing Nodes'] = df['Iteration'] - 1
    st.dataframe(df)
    for name in ss['policy_names']:
        st.header(name)
        title = alt.TitleParams("Resilience Chart", align='center', anchor="middle",
                                fontSize=20, subtitle=f"Chain Length 1000 - {name}",
                                subtitleFontSize=16)
        data = df[df['Policy'] == shorten_parameter_name(shorten_group_name(name))]
        data['Resilience (Moving Average)'] = data['Resilience'].rolling(10, min_periods=1).mean().tolist()
        tabs = st.tabs(['Chart', 'Data'])
        with tabs[0]:
            chart = (alt.Chart(data).mark_line()
                     .encode(x="Missing Nodes:Q",
                             y=alt.Y("Resilience (Moving Average):Q",
                                     title="Percent Reachable"))
                     .configure_legend(labelLimit=400)
                     .properties(title=title, height=400))
            st.altair_chart(chart)
        with tabs[1]:

            st.dataframe(data.drop(columns=['Iteration', 'Resilience', 'Policy', 'Scale', 'Density']), hide_index=True)

    pass


if __name__ == '__main__':
    resilience_report()
