from typing import Literal

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


class Heatmap:

    def __init__(self, df: pd.DataFrame, x: str, y: str, value_col: str, title: str, subtitle: str,
                 show_labels: bool = True,
                 log_scale: bool = False):
        self.df = df
        self.x = x
        self.y = y
        self.show_labels = show_labels
        self.title = title
        self.value_col = value_col
        self.log_scale = log_scale
        self.subtitle = subtitle

    def display(self):
        value_col = self.value_col
        value_col_name = value_col[:-2]
        y_col = self.y[:-2]
        scale_type: Literal['symlog', 'identity'] = "symlog" if self.log_scale else 'identity'
        df = self.df.copy()
        n_vals = df[y_col].nunique()
        time_max = df[value_col_name].max()
        time_min = df[value_col_name].min()
        if self.log_scale:
            proportion_col = (np.log((1 + self.df[value_col_name]) / (1 + time_min) + 1e-10)
                              / np.log((1 + time_max) / (1 + time_min) + 1e-10))
        else:
            proportion_col = (df[value_col_name] - time_min) / (time_max - max(time_min, 1)) \
                if time_min >= 1 else 0.5

        helper_df = df.assign(Proportion=proportion_col)
        title = alt.TitleParams(self.title, align='center', anchor="middle",
                                fontSize=20, subtitle=self.subtitle,
                                subtitleFontSize=18)
        base_chart = alt.Chart(helper_df, title=title).mark_rect().encode(
            x=self.x, y=self.y, color=alt.Color(value_col, scale=alt.Scale(scheme="viridis",
                                                                           domainMin=time_min,
                                                                           domainMax=max(1, time_max),
                                                                           type=scale_type), sort='descending'),
        )
        if self.show_labels:
            heatmap = (base_chart + base_chart.mark_text().encode(
                text=alt.Text(value_col, format=",.3"),
                color=(alt.when(alt.datum.Proportion < 0.5)
                       .then(alt.value('black')).otherwise(alt.value('white'))),
                size=alt.value(36),
            )).properties(height=75 * n_vals + 160).configure_axisY(labelLimit=800)
        else:
            heatmap = (base_chart.configure_axisX(labelLimit=800).configure_axisY(labelLimit=800)
                       .configure_legend(labelLimit=800))
        st.altair_chart(heatmap)
