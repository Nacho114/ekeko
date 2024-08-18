# -*- coding: utf-8 -*-
"""ekekoviz

A small library to plot financial stock data using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
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


def init_stock_plot(title):
    """Initialize a stock plot with a secondary y-axis."""
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


def add_volume(fig, stock_df):
    """Add volume bars to the plot."""
    colors = [
        COLORS["green"] if open < close else COLORS["red"]
        for open, close in zip(stock_df["Open"], stock_df["Close"])
    ]

    fig.add_trace(
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
    fig.update_yaxes(
        title_text="Volume",
        secondary_y=True,
        range=[0, stock_df["Volume"].max() * 5],  # Scale factor to adjust the height
        showgrid=False,
        zeroline=False,
    )

    # Update layout to adjust the margin between the main plot and volume plot
    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
        # height=700  # Adjust height as needed
    )

    return fig


def add_candlestick(fig, stock_df):
    """Add candlestick plot to the figure."""
    fig.add_trace(
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
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


def add_transactions(fig, transactions):
    """Add buy/sell markers to the plot."""
    buys = transactions[transactions["size"] > 0]
    sells = transactions[transactions["size"] < 0]

    fig.add_trace(
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

    fig.add_trace(
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

    return fig


def add_scatter(fig, df, color, visible="legendonly"):
    """Add scatter plot to the figure."""
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df,
            name=df.name,
            line=dict(color=color, width=2),
            visible=visible,
            hoverinfo="none",
        )
    )
    return fig


def get_stock_plot_fig(
    stock_df: pd.DataFrame,
    other_dfs: list[pd.Series] | None = None,
    transactions: pd.DataFrame | None = None,
    title="110",
):
    """Plot stock data with additional curves and buy/sell markers."""
    fig = init_stock_plot(title)

    ## ---------------------------------------------------------
    # Format time ----------------------------------------------
    ## ---------------------------------------------------------

    stock_df = stock_df.copy()
    stock_df.index = stock_df.index.strftime("%Y-%m-%d")

    tmp_other_dfs = []
    if other_dfs:
        for other_df in other_dfs:
            other_df = other_df.copy()
            other_df.index = other_df.index.strftime("%Y-%m-%d")
            tmp_other_dfs.append(other_df)
    other_dfs = tmp_other_dfs

    if transactions is not None:
        transactions = transactions.copy()
        transactions.index = transactions.index.strftime("%Y-%m-%d")

    ## ---------------------------------------------------------
    ## ---------------------------------------------------------
    ## ---------------------------------------------------------

    fig = add_candlestick(fig, stock_df)

    close_df = stock_df["Close"]
    close_df.name = stock_df["Close"].name
    fig = add_scatter(fig, close_df, "blue", "legendonly")

    curve_colors = ["yellow", "cyan", "magenta", "orange"]
    if other_dfs:
        for idx, other_df in enumerate(other_dfs):
            color_index = idx % len(curve_colors)
            fig = add_scatter(fig, other_df, curve_colors[color_index])

    fig = add_volume(fig, stock_df)

    if transactions is not None:
        fig = add_transactions(fig, transactions)

    return fig


def _with_style(fig):
    # Update layout with the custom color and grid settings
    fig.update_layout(
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        font=dict(color=COLORS["text"]),
        xaxis=dict(
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
    )

    # Make the scatter points bigger and more visible
    fig.update_traces(marker=dict(size=10, line=dict(width=2, color="palegreen")))
    fig.update_xaxes(linecolor=COLORS["background"])

    return fig


def line(x, y, labels, title):
    fig = px.line(x=x, y=y, labels=labels, title=title)
    return _with_style(fig)


def scatter(x, y, labels, title):
    """
    Creates a scatter plot with customized aesthetics.

    Args:
        x (list): x-axis values.
        y (list): y-axis values.
        labels (dict): A dictionary containing label configurations for the plot.
        title (str): The title of the plot.

    Returns:
        plotly.graph_objects.Figure: The configured plot.
    """
    # Create the scatter plot
    fig = px.scatter(x=x, y=y, labels=labels, title=title)

    return _with_style(fig)


def get_equity_curve_fig(portfolio: pd.DataFrame):
    fig = init_stock_plot("Equity curve")

    value = portfolio["normalized_value"]
    fig.add_trace(
        go.Scatter(
            x=value.index,
            y=value,
            name=value.name,
        )
    )

    cummax = portfolio["cummax"]
    fig.add_trace(
        go.Scatter(
            x=cummax.index,
            y=cummax,
            name=cummax.name,
        )
    )

    return fig
