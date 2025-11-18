import streamlit as st
from streamlit import session_state as ss

from components.Heatmap import Heatmap
from components.utils import *


def policy_growth_rate():
    if 'selected_policies' not in ss:
        st.switch_page("pages/3_Select_Policies.py")
    st.title("Policy Growth Rate")
    policies_selected = ss['selected_policies']
    density = ss['density']

    st.title("Cost Map")
    log_scale = ss['log_scale']
    partial_dfs = []
    for op in OP_NAMES_ABBREVIATED:
        partial_df = pd.DataFrame({'Mean':
                                       get_summary_data(policies_selected, 'Uniform', op,
                                                        SCALES.copy(), agg_func='mean'),
                                   'Operation': op})
        partial_df['Operation'] = partial_df['Operation'].replace(OP_NAMES_ABBREVIATED) + ' - IPFS Retrieves'
        partial_dfs.append(partial_df)

    partial_df = pd.DataFrame({'Mean':
                                   get_summary_data(policies_selected, 'Uniform', 'Store',
                                                    SCALES.copy(), actions=[Action.LINKS], agg_func='mean'),
                               'Operation': 'Add Node - Links'})
    partial_dfs.append(partial_df)
    df = pd.concat(partial_dfs).reset_index()

    df_policies = dict(tuple(df.groupby('Policy')))
    for name, df in df_policies.items():
        st.header(name)
        heatmap = Heatmap(df, 'Scale:O', 'Operation:O', 'Mean:Q',
                          'Number of Actions Required',
                          f'{name} - {density}', log_scale=log_scale)
        heatmap.display()


if __name__ == '__main__':
    policy_growth_rate()
