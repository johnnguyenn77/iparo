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
        self.x_sort = None
        self.y_sort = None

    def set_x_sort(self, x_sort):
        self.x_sort = x_sort

    def set_y_sort(self, y_sort):
        self.y_sort = y_sort

    def display(self):
        value_col = self.value_col
        value_col_name = value_col[:-2]
        x_col = self.x[:-2]
        y_col = self.y[:-2]
        scale_type: Literal['symlog', 'identity'] = "symlog" if self.log_scale else 'identity'
        df = self.df.copy()
        n_vals_x = df[x_col].nunique()
        n_vals_y = df[y_col].nunique()
        time_max = df[value_col_name].max()
        time_min = df[value_col_name].min()
        if self.log_scale:
            proportion_col = (np.log((1 + self.df[value_col_name]) / (1 + time_min) + 1e-10)
                              / np.log((1 + time_max) / (1 + time_min) + 1e-10))
        else:
            proportion_col = (df[value_col_name] - time_min) / (time_max - max(time_min, 1)) \
                if time_max >= max(time_min, 1) else 0.5

        helper_df = df.assign(Proportion=proportion_col)
        title = alt.TitleParams(" ", align='center', anchor="middle",
                                fontSize=20, subtitleFontSize=18)
        base_chart = alt.Chart(helper_df, title=title).mark_rect().encode(
            x=alt.X(self.x, title=x_col, sort=self.x_sort),
            y=alt.Y(self.y, title=y_col, sort=self.y_sort),
            color=alt.Color(value_col, scale=alt.Scale(scheme="viridis",
                                                       domainMin=time_min,
                                                       domainMax=max(1, time_max),
                                                       type=scale_type), sort='descending',
                            legend=alt.Legend(titleColor='black',
                                              labelColor='black',
                                              titleFontSize=16)),
        )
        if self.show_labels:
            heatmap = ((base_chart + base_chart.mark_text().encode(
                text=alt.Text(value_col, format=",.3"),
                color=(alt.when(alt.datum.Proportion < 0.5)
                       .then(alt.value('black')).otherwise(alt.value('white'))),
                size=alt.value(36),
            )).configure_axis(labelFontSize=16, labelColor='black', titleColor='black', titleFontSize=16)
                       .properties(height=70 * n_vals_y + 160, width=200 * n_vals_x)
                       .configure_axisX(labelLimit=800)
                       .configure_axisY(labelLimit=800, titlePadding=30))
        else:
            heatmap = (base_chart.configure_axisX(labelLimit=800).configure_axisY(labelLimit=800)
                       .configure_axis(labelFontSize=12, labelColor='black', titleColor='black', titleFontSize=16)
                       .configure_legend(labelLimit=1600))

        st.altair_chart(heatmap, use_container_width=False)
