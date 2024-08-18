import pandas as pd
from ekeko.plotting.plot_builder import PlotBuilder, init_fig_with_style
import plotly.graph_objects as go


def get_stock_plot_fig(
    stock_df: pd.DataFrame,
    other_dfs: list[pd.Series] | None = None,
    transactions: pd.DataFrame | None = None,
    title="110",
):

    plot_builder = PlotBuilder(title)

    ## ---------------------------------------------------------
    # Format time ----------------------------------------------
    ## ---------------------------------------------------------

    stock_df = stock_df.copy()
    assert isinstance(stock_df.index, pd.DatetimeIndex)
    stock_df.index = stock_df.index.strftime("%Y-%m-%d")

    tmp_other_dfs = []
    if other_dfs:
        for other_df in other_dfs:
            other_df = other_df.copy()
            assert isinstance(other_df.index, pd.DatetimeIndex)
            other_df.index = other_df.index.strftime("%Y-%m-%d")
            tmp_other_dfs.append(other_df)
    other_dfs = tmp_other_dfs

    if transactions is not None:
        transactions = transactions.copy()
        assert isinstance(transactions.index, pd.DatetimeIndex)
        transactions.index = transactions.index.strftime("%Y-%m-%d")

    ## ---------------------------------------------------------
    ## ---------------------------------------------------------
    ## ---------------------------------------------------------

    plot_builder.add_candlestick(stock_df)

    close_df = stock_df["Close"]
    close_df.name = stock_df["Close"].name
    plot_builder.add_scatter(close_df, "blue", "legendonly")

    curve_colors = ["yellow", "cyan", "magenta", "orange"]
    if other_dfs:
        for idx, other_df in enumerate(other_dfs):
            color_index = idx % len(curve_colors)
            plot_builder.add_scatter(other_df, curve_colors[color_index])

    plot_builder.add_volume(stock_df)

    if transactions is not None:
        plot_builder.add_transactions(transactions)

    return plot_builder.build()


def get_equity_curve_fig(portfolio: pd.DataFrame, title="Equity Curve"):
    fig = init_fig_with_style(title)

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
