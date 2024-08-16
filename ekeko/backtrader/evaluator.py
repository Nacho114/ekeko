import pandas as pd
import numpy as np
from ekeko.backtrader.broker import OrderAction, Transaction, Trade
from ekeko.backtrader.engine import Engine
from ekeko.core.types import Ticker


class Evaluator:

    def __init__(self, engine: Engine):
        self.account = engine.broker.account
        self.value_df = self.account.value_df
        self.transactions_df = self.__transactions_to_dataframe(
            self.account.transactions
        )
        self.trades_df = self.__trades_to_dataframe(self.account.trades)
        self.signal_dfs = engine.signal_dfs

    def print_stats(self):
        pd.set_option("display.max_columns", None)
        print("Values")
        print(self.value_df)
        print("Transactions")
        print(self.transactions_df)
        print()
        print("Trades")
        self.__print_trades()

    def get_indicators(self, ticker: Ticker) -> list[pd.Series]:
        indicator = []
        signal = self.signal_dfs[ticker]
        for column in signal.columns:
            if column not in ["buy", "sell"]:
                df = pd.DataFrame({column: signal[column]})
                df = signal[column].copy()
                indicator.append(df)

        return indicator

    def transactions_for_plotting(self, ticker: Ticker) -> pd.DataFrame:

        # Filter the dataframe for the given ticker
        df = self.transactions_df
        ticker_df = df[df["ticker"] == ticker].copy()

        # Convert date to datetime and set as index
        ticker_df["date"] = pd.to_datetime(ticker_df["date"])
        ticker_df.set_index("date", inplace=True)

        # Create size column (positive for buy, negative for sell)
        ticker_df["size"] = np.where(
            ticker_df["order_action"] == OrderAction.BUY,
            ticker_df["quantity"],
            -ticker_df["quantity"],
        )

        # Create value column (negative for buy, positive for sell)
        ticker_df["value"] = -ticker_df["size"] * ticker_df["execution_price"]

        # Select and reorder columns
        result_df = ticker_df[["size", "execution_price", "value"]]
        result_df.columns = ["size", "price", "value"]

        assert isinstance(result_df, pd.DataFrame)

        return result_df

    def __transactions_to_dataframe(
        self, transactions: list[Transaction]
    ) -> pd.DataFrame:
        data = []
        for transaction in transactions:
            data.append(
                {
                    "date": transaction.execution_date,
                    "ticker": transaction.order.ticker,
                    "order_action": transaction.order.order_action,
                    "quantity": transaction.order.quantity,
                    "execution_price": transaction.execution_price,
                    "commission": transaction.comission,
                }
            )

        return pd.DataFrame(data)

    def __print_trades(self):
        df_sorted = self.trades_df.sort_values(by='pnl')
        columns_to_print = ['ticker', 'closing_date', 'pnl']
        print(df_sorted[columns_to_print])

    def __trades_to_dataframe(self, trades: list[Trade]) -> pd.DataFrame:
        data = []
        for trade in trades:
            data.append(
                {
                    "ticker": trade.opening_transaction.order.ticker,
                    "opening_date": trade.opening_transaction.execution_date,
                    "closing_date": trade.closing_transaction.execution_date,
                    "commission": trade.comission,
                    "pnl": trade.pnl,
                    "pnl_without_commission": trade.pnl_without_comission,
                }
            )

        return pd.DataFrame(data)
