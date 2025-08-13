import pandas as pd
import altair as alt
import streamlit as st

from components.utils import COLOR_SCHEME


class LayeredBoxPlot:

    def __init__(self, summary: pd.DataFrame, title: str, y_title: str, x: str, column: str, color: str,
                 log_scale: bool):
        """
        The summary is the concatenation of DataFrames generated from the df.summary() method,
        transposed with a unique index.
        :param title: The title of the graph.
        :param y_title: The title of the dependent variable to plot.
        :param x: The nominal variable to plot, using an Altair encoding.
        :param log_scale: Whether to display the graph in the logarithmic scale.
        :param column: The column variable.
        :param color: The color variable.
        """
        if log_scale:
            y_title += " (Log)"

        n = summary[x.split(":")[0]].nunique()
        self.chart = (alt.LayerChart(summary).encode(
            color=alt.Color(color, legend=alt.Legend(labelLimit=400), scale=alt.Scale(scheme=COLOR_SCHEME)),
            x=x, tooltip=[color, alt.Tooltip("count:Q", format=","),
                          alt.Tooltip("mean:Q", format=",.2f"),
                          alt.Tooltip("min:Q", format=","), alt.Tooltip("q1:Q", format=",.2f"),
                          alt.Tooltip("median:Q", format=",.2f"), alt.Tooltip("q3:Q", format=",.2f"),
                          alt.Tooltip("max:Q", format=",")],
        ).add_layers(
            alt.Chart().mark_rule(size=2).encode(y="min:Q", y2="max:Q"),
            alt.Chart().mark_bar(width=20, opacity=0.5).encode(y="q1:Q", y2="q3:Q"),
            alt.Chart().mark_tick(width=30, thickness=2).encode(y="median:Q"),
            alt.Chart().mark_circle(size=50).encode(
                y=alt.Y("mean:Q", axis=alt.Axis(format="~s"),
                        scale=alt.Scale(type="symlog" if log_scale else 'identity'),
                        title=y_title))
        )).properties(width=35 * n).facet(column=column, title=alt.TitleParams(title, align='center', anchor="middle", fontSize=20))

    def display(self):
        st.altair_chart(self.chart, use_container_width=True)
