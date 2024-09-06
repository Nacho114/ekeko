from pathlib import Path
import ekeko
from ekeko.backtrader.broker import (
    Account,
    BrokerBuilder,
    Order,
    OrderBuilder,
    Position,
)
from ekeko.backtrader.engine import Engine
from ekeko.backtrader.screener import TrivialScreener, YfinanceTickerSceener
from ekeko.data_loader import YfDataset
from ekeko.core.signal_type import ENTRY, EXIT, PLOT_COLUMNS

from ekeko.core import Ticker, Date, Number

import pandas as pd

class Strategy:
    def __init__(self):
        self.short_window = 12
        self.long_window = 26

    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        # Initialize signal DataFrame
        signal = pd.DataFrame(index=stock_df.index)

        # Calculate short and long EMAs and add to signal DataFrame
        signal["EMA_short"] = (
            stock_df["Close"].ewm(span=self.short_window, adjust=False).mean()
        )
        signal["EMA_long"] = (
            stock_df["Close"].ewm(span=self.long_window, adjust=False).mean()
        )

        # Generate buy and sell signals
        signal[ENTRY] = (signal["EMA_short"] > signal["EMA_long"]) & (
            signal["EMA_short"].shift(1) <= signal["EMA_long"].shift(1)
        )
        signal[EXIT] = (signal["EMA_short"] < signal["EMA_long"]) & (
            signal["EMA_short"].shift(1) >= signal["EMA_long"].shift(1)
        )

        signal.attrs[PLOT_COLUMNS] = ["EMA_short", "EMA_long"]

        return signal


class Trader:

    def trade(
        self,
        account: Account,
        date: Date,
        ticker: Ticker,
        signal: pd.DataFrame,
        stock_row: pd.DataFrame,
        open_positions: list[Position],
    ) -> list[Order]:
        _ = stock_row  # We don't use price action in Market order
        orders = []

        if signal.loc[ENTRY] and len(open_positions) == 0:

            # Note, if price tomorrow is different, then the quantity might not
            # be appropriate

            quantity = account.get_cash(date) * 0.1 / stock_row.loc['Close']

            order = OrderBuilder(ticker, quantity).market().buy().at_date(date).build()
            orders.append(order)

        if signal.loc["exit"]:
            for p in open_positions:
                order = p.get_closing_order(date)
                orders.append(order)

        return orders


class Slippage:

    def compute(self, stock_df_row: pd.DataFrame) -> Number:
        return stock_df_row.loc["Close"]


if __name__ == "__main__":

    ekeko.config.set_num_processors(6)
    period = "2y"

    dataset = YfDataset(["GPS", "CAVA", "AFJK"], TrivialScreener(), period)
    dataset.set_cached_tickers(Path('/tmp/'))
    stock_dfs = dataset.load()

    comission = 0.01
    initial_cash = 10000

    broker_builder = BrokerBuilder(initial_cash, comission, stock_dfs, Slippage())
    engine = Engine(Trader(), Strategy(), broker_builder)

    report = engine.run()
    
    report.add_ticker_to_benchmark('QQQ', period)
    report.add_sceener_index_to_benchmark(stock_dfs)
    report.print()
    # report.print_transactions_and_trades()

    # report.plot_equity_curve()
