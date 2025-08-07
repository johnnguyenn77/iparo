import pandas as pd
import altair as alt
import streamlit as st

from components.utils import COLOR_SCHEME


class LayeredBoxPlot:

    def __init__(self, summary: pd.DataFrame, title: str, y_title: str, x: str, n: int, n_cols: int,
                 column: str, row: str, color: str,
                 log_scale: bool):
        """
        The summary is the concatenation of DataFrames generated from the df.summary() method,
        transposed with a unique index.
        :param title: The title of the graph.
        :param y_title: The title of the dependent variable to plot.
        :param x: The nominal variable to plot, using an Altair encoding.
        :param log_scale: Whether to display the graph in the logarithmic scale.
        :param n: The number of nominal variables to display.
        :param n_cols: The number of columns to display if there is only one nominal variable.
        :param column: The column variable in the facet chart.
        :param row: The row variable in the facet chart.
        """
        if log_scale:
            y_title += " (Log)"

        base = (alt.LayerChart(summary).encode(
            color=alt.Color(color, legend=alt.Legend(labelLimit=400), scale=alt.Scale(scheme=COLOR_SCHEME)),
            tooltip=[color, alt.Tooltip("count:Q", format=","),
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

        # If the number of nominal variables is greater than 1, then use the variables in each facet.
        if n > 1 and n_cols > 1:
            self.chart = base.encode(x=x).facet(column=column,
                                                row=row,
                                                title=alt.TitleParams(title, align='center', anchor="middle",
                                                                      fontSize=20)
                                                ).configure_axisX(labelLimit=400)
        # Otherwise, if number of columns > 1, use the column variable as X and row variable as column.
        elif n_cols > 1:
            self.chart = (base.encode(x=column)
                          .facet(column=row, title=alt.TitleParams(title, align='center',
                                                                   anchor="middle", fontSize=20)
                                 ).configure_axisX(labelLimit=400))
        else:
            # We will assume number of nominals > 1 and rows > 1
            self.chart = (base.encode(x=x)
                          .facet(column=row, title=alt.TitleParams(title, align='center',
                                                                   anchor="middle", fontSize=20)
                                 ).configure_axisX(labelLimit=400))
        self.chart.spec.width = 35 * n if n > 1 else 35 * n_cols

    def display(self):
        st.altair_chart(self.chart, use_container_width=True)
