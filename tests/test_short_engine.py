from ekeko.backtrader.broker import (
    Account,
    BrokerBuilder,
    Order,
    OrderBuilder,
    Position,
)
from ekeko.backtrader.engine import Engine

from ekeko.core import Ticker, Date, Number

import pandas as pd


class Strategy:

    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        signal = pd.DataFrame(index=stock_df.index)

        signal["sell"] = stock_df["Close"] == 3

        signal["buy"] = stock_df["Close"] == 2

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

        if signal.loc["sell"] and len(open_positions) == 0:

            # Note, if price tomorrow is different, then the quantity might not
            # be appropriate

            # quantity = account.get_cash(date) * 0.1 / stock_row.loc['Close']
            quantity = 2

            order = OrderBuilder(ticker, quantity).market().sell().at_date(date).build()
            
            orders.append(order)

        if signal.loc["buy"]:
            for p in open_positions:
                order = p.get_closing_order(date)
                orders.append(order)

        return orders


class Slippage:

    def compute(self, stock_df_row: pd.DataFrame) -> Number:
        return stock_df_row.loc["Close"]


def test_engine():  # Test cases

    data_a = {
        "Close": [3, 4, 2, 50, 3, 4, 2, 10],
    }
    index = pd.to_datetime(
        [
            "2023-08-01",
            "2023-08-02",
            "2023-08-03",
            "2023-08-04",
            "2023-08-05",
            "2023-08-06",
            "2023-08-07",
            "2023-08-08",
        ]
    )
    stock_df_a = pd.DataFrame(data_a, index=index)
    ticker_a = "Aurora"

    stock_dfs = {ticker_a: stock_df_a}

    comission = 0.01
    initial_cash = 100

    broker_builder = BrokerBuilder(initial_cash, comission, stock_dfs, Slippage())
    engine = Engine(Trader(), Strategy(), broker_builder)

    report = engine.run()

    # report.print()
    # report.print_transactions_and_trades()
