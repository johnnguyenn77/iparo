from typing import Callable

import pandas as pd
import altair as alt
import streamlit as st

from components.utils import SCALES


class LayeredBoxPlot:

    def __init__(self, summary: pd.DataFrame, title: str, x: str, y_title: str, log_scale: bool, n: int):
        """
        The summary is the concatenation of DataFrames generated from the df.summary() method,
        transposed with a unique index.
        :param title: The title of the graph.
        :param x: The nominal variable to plot, using an Altair encoding.
        :param y_title: The title of the dependent variable to plot.
        :param log_scale: Whether to display the graph in the logarithmic scale.
        :param n: The number of nominal variables to display.
        """
        if log_scale:
            y_title += " (Log)"

        self.data = summary
        self.data.loc[self.data.Param == 'None', 'Policy'] = self.data.Group
        self.data.loc[self.data.Param != 'None', 'Policy'] = self.data.Group + " - " + self.data.Param

        base = (alt.LayerChart(summary).encode(
            color=alt.Color(x, legend=alt.Legend(labelLimit=400)),
            tooltip=[x, alt.Tooltip("count:Q", format=","),
                     alt.Tooltip("mean:Q", format=",.2f"),
                     alt.Tooltip("min:Q", format=","), alt.Tooltip("q1:Q", format=",.2f"),
                     alt.Tooltip("median:Q", format=",.2f"), alt.Tooltip("q3:Q", format=",.2f"),
                     alt.Tooltip("max:Q", format=",")]
        ).add_layers(
            alt.Chart().mark_rule(size=2).encode(y="min:Q", y2="max:Q"),
            alt.Chart().mark_bar(width=20, opacity=0.5).encode(y="q1:Q", y2="q3:Q"),
            alt.Chart().mark_tick(width=30, thickness=2).encode(y="median:Q"),
            alt.Chart().mark_circle(size=50).encode(
                y=alt.Y("mean:Q", axis=alt.Axis(format="~s"),
                        scale=alt.Scale(type="symlog" if log_scale else 'identity'),
                        title=y_title))
        ))
        if n > 1:
            self.chart = base.encode(x=x).facet(column=alt.Column("Scale:N", sort=SCALES),
                                                row="Density:N",
                                                title=alt.TitleParams(title, align='center', anchor="middle",
                                                                      fontSize=20)
                                                ).configure_axisX(labelLimit=400)

        else:
            self.chart = (base.encode(x=alt.X("Scale:N", sort=SCALES))
                          .facet(column="Density:N", title=alt.TitleParams(title, align='center',
                                                                           anchor="middle", fontSize=20)
                                 ).configure_axisX(labelLimit=400))
        self.chart.spec.width = 35 * len(SCALES) * n
        
        self.chart2 = alt.LayerChart(summary).encode(
            x="Scale:O",
            color=alt.Color(x, legend=alt.Legend(labelLimit=400)),
            tooltip=[x, alt.Tooltip("count:Q", format=","),
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
        ).facet(column=x, row="Density:N",
                title=alt.TitleParams(title, align='center', anchor="middle", fontSize=20)
                ).configure_axisX(labelLimit=400)
        self.chart2.spec.width = 200

    def display(self):
        tabs = st.tabs(["Results By Scale 📈", "Results by Policy 📈", "Summary Data 🔢"])
        with tabs[0]:
            st.altair_chart(self.chart, use_container_width=True)
        with tabs[1]:
            st.altair_chart(self.chart2, use_container_width=True)
        with tabs[2]:
            display_data = self.data.drop(columns=self.data.index.names)
            display_data.reset_index(inplace=True)
            display_data.set_index(['Policy', 'Scale', 'Density'], inplace=True)
            display_data.drop(columns=['Group', 'Param'], inplace=True)
            st.dataframe(display_data)
