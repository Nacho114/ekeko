# -*- coding: utf-8 -*-
"""ekekoviz

A small library to plot financial stock data using Plotly.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Configuration section for colors and styling
COLORS = {
    "background": "#22262f",
    "text": "#8f98af",
    "grid_line": "#323641",
    "green": "#30cc5a",
    "red": "#f03538",
}
GRID_N_TICKS = 10


def init_fig_with_style(title: str) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        hovermode="x",
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        xaxis=dict(
            type="category",
            tickformat="%b %Y",
            showgrid=True,
            gridcolor=COLORS["grid_line"],
            gridwidth=1,
            griddash="dot",
            nticks=GRID_N_TICKS,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["grid_line"],
            gridwidth=1,
            griddash="dot",
            nticks=GRID_N_TICKS,
        ),
        yaxis2=dict(
            showgrid=False,
        ),
        font=dict(color=COLORS["text"]),
    )
    return fig


class PlotBuilder:

    def __init__(self, title="Awesome plot!"):
        self.fig = init_fig_with_style(title)

    def add_volume(self, stock_df: pd.DataFrame):
        """Add volume bars to the plot."""
        colors = [
            COLORS["green"] if open < close else COLORS["red"]
            for open, close in zip(stock_df["Open"], stock_df["Close"])
        ]

        self.fig.add_trace(
            go.Bar(
                x=stock_df.index,
                y=stock_df["Volume"],
                marker_color=colors,
                marker_line_width=0,
                name="Volume",
                hoverinfo="none",
                opacity=0.6,
                visible=True,
            ),
            secondary_y=True,
        )

        # Update the secondary y-axis range to be at most 15% of the plot height
        self.fig.update_yaxes(
            title_text="Volume",
            secondary_y=True,
            range=[
                0,
                stock_df["Volume"].max() * 5,
            ],  # Scale factor to adjust the height
            showgrid=False,
            zeroline=False,
        )

        # Update layout to adjust the margin between the main plot and volume plot
        self.fig.update_layout(
            margin=dict(l=50, r=50, t=50, b=50),
            # height=700  # Adjust height as needed
        )

    def add_candlestick(self, stock_df: pd.DataFrame):
        """Add candlestick plot to the figure."""
        self.fig.add_trace(
            go.Candlestick(
                x=stock_df.index,
                open=stock_df["Open"],
                high=stock_df["High"],
                low=stock_df["Low"],
                close=stock_df["Close"],
                increasing_line_color=COLORS["green"],
                decreasing_line_color=COLORS["red"],
                name="Candlestick",
                visible=True,
            )
        )
        self.fig.update_layout(xaxis_rangeslider_visible=False)

    def add_transactions(self, transactions: pd.DataFrame):
        """Add buy/sell markers to the plot."""
        buys = transactions[transactions["size"] > 0]
        sells = transactions[transactions["size"] < 0]

        self.fig.add_trace(
            go.Scatter(
                x=buys.index,
                y=buys["price"],
                mode="markers",
                marker=dict(
                    symbol="triangle-up",
                    size=14,
                    color=COLORS["green"],
                    line=dict(color="black", width=2.5),  # Adding black border
                ),
                name="Buy",
                hoverinfo="text",
                text=[
                    f"Buy<br>Price: {price}<br>Size: {size}"
                    for price, size in zip(buys["price"], buys["size"])
                ],
            )
        )

        self.fig.add_trace(
            go.Scatter(
                x=sells.index,
                y=sells["price"],
                mode="markers",
                marker=dict(
                    symbol="triangle-down",
                    size=14,
                    color=COLORS["red"],
                    line=dict(color="black", width=2.5),  # Adding black border
                ),
                name="Sell",
                hoverinfo="text",
                text=[
                    f"Sell<br>Price: {price}<br>Size: {size}"
                    for price, size in zip(sells["price"], sells["size"])
                ],
            )
        )

    def add_scatter(
        self, df: pd.DataFrame | pd.Series, color: str, visible="legendonly"
    ):
        """Add scatter plot to the figure."""
        self.fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df,
                name=df.name,
                line=dict(color=color, width=2),
                visible=visible,
                hoverinfo="none",
            )
        )

    def build(self) -> go.Figure:
        return self.fig
