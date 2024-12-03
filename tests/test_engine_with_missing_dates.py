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


def assert_account_values(engine):
    # Define the expected values
    expected_data = {
        "cash": [100.0, 100.0, 100.0, 96.0, 96.0, 96.0, 96.0, 100.0, 100.0],
        "open_position": [0.0, 0.0, 0.0, 4.0, 4.0, 4.0, 4.0, 0.0, 0.0],
        "value": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "normalized_value": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        "cummax": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    }

    # Convert to a DataFrame with the appropriate index
    expected_df = pd.DataFrame(
        expected_data,
        index=pd.date_range(start="2023-01-01", periods=len(expected_data["cash"]), freq="D")
    )

    # Ensure both DataFrames have consistent dtypes
    expected_df = expected_df.astype("float64")
    actual_df = engine.broker.account.value_df.astype("float64")

    # Assert that the actual and expected DataFrames are equal
    pd.testing.assert_frame_equal(actual_df, expected_df)

def test_engine_with_missing_dates():  # Test cases

    # Stock A has data for all dates
    data_a = {
        "Close": [1, 1, 1, 1, 1, 1, 1, 1, 1],
    }
    index_a = pd.date_range(start="2023-01-01", periods=len(data_a["Close"]), freq='D')
    stock_df_a = pd.DataFrame(data_a, index=index_a)
    ticker_a = "Aurora"

    # Stock B has data for only certain dates
    data_b = {
        "Close": [2, 4, 4, 4],  # Signal generated at index 2, executed at index 4
    }
    index_b = pd.to_datetime(["2023-01-02", "2023-01-04", "2023-01-06", "2023-01-08"])
    stock_df_b = pd.DataFrame(data_b, index=index_b)
    ticker_b = "Baltigo"

    stock_dfs = {ticker_a: stock_df_a, ticker_b: stock_df_b}

    # Parameters
    comission = 0
    initial_cash = 100

    # Define the broker, engine, and components
    broker_builder = BrokerBuilder(initial_cash, comission, stock_dfs, Slippage())
    engine = Engine(Trader(), Strategy(), broker_builder)

    # Run the engine and generate the report
    report = engine.run()

    # Output the results for validation
    # report.print()
    # report.print_transactions_and_trades()

    assert_account_values(engine)

