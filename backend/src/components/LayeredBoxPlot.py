from typing import Callable

import pandas as pd
import altair as alt
import streamlit as st

from components.Component import Component
from components.utils import SCALES, DENSITIES, SCALES_DICT, drop_index_cols


class LayeredBoxPlot(Component):

    def __init__(self, summary: pd.DataFrame, title: str, x: str, y_title: str, log_scale: bool):
        """
        The summary is the concatenation of DataFrames generated from the df.summary() method,
        transposed with a unique index.
        :param title: The title of the graph.
        :param x: The nominal variable to plot, using an Altair encoding.
        :param y_title: The title of the dependent variable to plot.
        :param log_scale: Whether to display the graph in the logarithmic scale.
        """
        if log_scale:
            y_title += " (Log)"

        self.data = summary
        self.chart = alt.LayerChart(summary).encode(
            x=x,
            color=alt.Color(x),
            tooltip=[x, alt.Tooltip("count:Q", format=","),
                     alt.Tooltip("mean:Q", format=",.2f"),
                     alt.Tooltip("min:Q", format=","), alt.Tooltip("q1:Q", format=",.2f"),
                     alt.Tooltip("median:Q", format=",.2f"), alt.Tooltip("q3:Q", format=",.2f"),
                     alt.Tooltip("max:Q", format=",")],
        ).add_layers(
            alt.Chart().mark_rule(size=2).encode(y="min:Q", y2="max:Q"),
            alt.Chart().mark_bar(width=30, opacity=0.5).encode(y="q1:Q", y2="q3:Q"),
            alt.Chart().mark_tick(width=40, thickness=2).encode(y="median:Q"),
            alt.Chart().mark_circle(size=50).encode(
                y=alt.Y("mean:Q", axis=alt.Axis(format="~s"),
                        scale=alt.Scale(type="symlog" if log_scale else 'identity'),
                        title=y_title))
        ).facet(column=alt.Column("Scale:N", sort=SCALES), row="Density:N", title=title)
        # proportional to number of rows, divided by the number of scales and the number of densities.
        self.chart.spec.width = 45 * summary.shape[0] / (len(SCALES) * len(DENSITIES))

    def display(self):

        tabs = st.tabs(["Results By Strategy 📈", "Summary Data 🔢"])
        with tabs[0]:
            st.altair_chart(self.chart, use_container_width=True)
        with tabs[1]:
            st.dataframe(drop_index_cols(self.data))
