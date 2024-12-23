import pandas as pd
from ekeko.core.signal_type import *
from ekeko.plotting.plot_builder import PlotBuilder, init_fig_with_style
import plotly.graph_objects as go


def __add_signal(
    plot_builder: PlotBuilder, signal: pd.DataFrame, entry_exit_height: float
):
    signal = signal.copy()
    assert isinstance(signal.index, pd.DatetimeIndex)
    signal.index = signal.index.strftime("%Y-%m-%d")

    for col in signal.attrs.get(PLOT_COLUMNS, []):
        plot_builder.add_scatter(signal[col])

    entry_signal = signal.get(ENTRY, None)
    if not entry_signal is None:
        plot_builder.add_dots(
            entry_signal, entry_exit_height, color="green", name=ENTRY
        )

    exit_signal = signal.get(EXIT, None)
    if not exit_signal is None:
        plot_builder.add_dots(exit_signal, entry_exit_height, color="red", name=EXIT)


def __add_transactions(plot_builder: PlotBuilder, transactions: pd.DataFrame):
    transactions = transactions.copy()
    assert isinstance(transactions.index, pd.DatetimeIndex)
    transactions.index = transactions.index.strftime("%Y-%m-%d")

    plot_builder.add_transactions(transactions)


def get_stock_plot_fig(
    stock_df: pd.DataFrame,
    signal: pd.DataFrame | None = None,
    transactions: pd.DataFrame | None = None,
    title="110",
):

    plot_builder = PlotBuilder(title)

    stock_df = stock_df.copy()
    assert isinstance(stock_df.index, pd.DatetimeIndex)
    stock_df.index = stock_df.index.strftime("%Y-%m-%d")

    plot_builder.add_candlestick(stock_df)

    close_df = stock_df["Close"]
    close_df.name = stock_df["Close"].name
    blue = "#636efa"
    plot_builder.add_scatter(close_df, blue, "legendonly")

    if isinstance(signal, pd.DataFrame):
        entry_exit_height = stock_df["Close"].max() * 0.8
        __add_signal(plot_builder, signal, entry_exit_height)

    if isinstance(transactions, pd.DataFrame):
        __add_transactions(plot_builder, transactions)

    plot_builder.add_volume(stock_df)

    return plot_builder.build()


def get_equity_curve_fig(
    portfolio: pd.DataFrame,
    benchmark_dfs: list[pd.DataFrame] = [],
    title="Equity Curve",
):
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
            x=value.index,
            y=cummax,
            name=cummax.name,
        )
    )

    for df in benchmark_dfs:
        fig.add_trace(
            go.Scatter(
                x=value.index,
                y=df,
                name=df.name,
                visible="legendonly",
            )
        )

    return fig
