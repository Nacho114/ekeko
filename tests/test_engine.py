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

        signal["buy"] = stock_df["Close"] == 2

        signal["sell"] = stock_df["Close"] == 3

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

        if signal.loc["buy"] and len(open_positions) == 0:

            # Note, if price tomorrow is different, then the quantity might not
            # be appropriate

            # quantity = account.get_cash(date) * 0.1 / stock_row.loc['Close']
            quantity = 1

            order = OrderBuilder(ticker, quantity).market().buy().at_date(date).build()

            orders.append(order)

        if signal.loc["sell"]:
            for p in open_positions:
                order = p.get_closing_order(date)
                orders.append(order)

        return orders


class Slippage:

    def compute(self, stock_df_row: pd.DataFrame) -> Number:
        return stock_df_row.loc["Close"]


def test_engine():  # Test cases

    data_a = {
        "Close": [2, 4, 1, 3, 5, 7, 2, 10, 3, 7],
    }
    # Function to generate a datetime index based on "Close" data
    def generate_datetime_index(data, start_date="2023-01-01"):
        close_prices = data.get("Close", [])
        return pd.date_range(start=start_date, periods=len(close_prices), freq='D')

    index = generate_datetime_index(data_a)
    stock_df_a = pd.DataFrame(data_a, index=index)
    ticker_a = "Aurora"

    stock_dfs = {ticker_a: stock_df_a}


    comission = 0.01
    initial_cash = 100

    broker_builder = BrokerBuilder(initial_cash, comission, stock_dfs, Slippage())
    engine = Engine(Trader(), Strategy(), broker_builder)

    report = engine.run()
    report.print()
    report.print_transactions_and_trades()
