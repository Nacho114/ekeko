import pandas as pd
from ekeko.backtrader.broker import OrderAction, Transaction, Trade
from ekeko.backtrader.engine import Engine
from ekeko.core.types import Date, Ticker


class Evaluator:

    def __init__(self, engine: Engine):
        self.account = engine.broker.account
        value_df = self.account.value_df.copy()
        self.__extend_value_df(value_df)
        self.value_df = value_df
        self.transactions_df = self.__transactions_to_dataframe(
            self.account.transactions
        )
        self.trades_df = self.__trades_to_dataframe(self.account.trades)
        self.signal_dfs = engine.signal_dfs

    def print_stats(self):
        pd.set_option("display.max_columns", None)
        print("Transactions")
        print(self.value_df)
        print("Transactions")
        print(self.transactions_df)
        self.__print_trades()
        self.__print_portfolio_value()

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

        # Create value column (negative for buy, positive for sell)
        ticker_df["value"] = -ticker_df["size"] * ticker_df["execution_price"]

        # Select and reorder columns
        result_df = ticker_df[["size", "execution_price", "value", "commission"]]
        result_df.columns = ["size", "price", "value", "commission"]

        assert isinstance(result_df, pd.DataFrame)

        return result_df

    def __transactions_to_dataframe(
        self, transactions: list[Transaction]
    ) -> pd.DataFrame:
        data = []
        for transaction in transactions:
            sign = 1 if transaction.order.order_action == OrderAction.BUY else -1
            data.append(
                {
                    "date": transaction.execution_date,
                    "ticker": transaction.order.ticker,
                    "size": transaction.order.quantity * sign,
                    "execution_price": transaction.execution_price,
                    "commission": transaction.comission,
                }
            )

        return pd.DataFrame(data)

    def __print_portfolio_value(self):
        print('\nPortfolio\n')
        last_row = self.value_df.iloc[-1]
        initial_cash = self.value_df.iloc[0]['cash']
        final_value = last_row['value']
        percentage_growth = ((final_value - initial_cash) / initial_cash) * 100

        last_row_dict = last_row.to_dict()

        print(f"initial cash{'':8} {initial_cash:.4f}")
        for key, value in last_row_dict.items():
            print(f"{key:20} {value:.4f}")

        print("\nPercentage growth (last value w.r.t initial cash): {:.2f}%\n".format(percentage_growth))

    def __print_trades(self):
        df_sorted = self.trades_df.sort_values(by='pnl', ascending=False)
        columns_to_print = ['ticker', 'duration', 'pnl', 'commission']
        print('\nTrades\n')
        print(df_sorted[columns_to_print])

        df = df_sorted

        total_trades = len(df)

        avg_pnl = df['pnl'].mean()

        avg_duration = df['duration'].mean()

        positive_pnl = df[df['pnl'] > 0]['pnl']
        avg_positive_pnl = positive_pnl.mean()

        negative_pnl = df[df['pnl'] < 0]['pnl']
        avg_negative_pnl = negative_pnl.mean()

        num_positive = len(positive_pnl)

        num_negative = len(negative_pnl)

        pain_gain_ratio = avg_positive_pnl / abs(avg_negative_pnl)

        print("\nTrade statistics\n")
        print(f"Number of trades: {total_trades}")
        print(f"Average PNL: {avg_pnl:.2f}")
        print(f"Average open position: {avg_duration:.2f} days")
        print(f"Average Positive PNL: {avg_positive_pnl:.2f}")
        print(f"Average Negative PNL: {avg_negative_pnl:.2f}")
        print(f"Number of Positive PNL Trades: {num_positive}")
        print(f"Number of Negative PNL Trades: {num_negative}")
        print(f"Pain/Gain Ratio: {pain_gain_ratio:.2f}")
        print()


    def __extend_value_df(self, value_df: pd.DataFrame):
        value_df['value'] = value_df['cash'] + value_df['open_position']
        value_df['normalized_value'] = value_df['value'] / value_df.iloc[0]['cash']

    def __trades_to_dataframe(self, trades: list[Trade]) -> pd.DataFrame:
        def get_duration(start: Date, end: Date):
            duration = pd.to_datetime(end) - pd.to_datetime(start)
            return duration.days

        data = []
        for trade in trades:
            duration = get_duration(trade.opening_transaction.execution_date, trade.closing_transaction.execution_date)
            data.append(
                {
                    "ticker": trade.opening_transaction.order.ticker,
                    "pnl": trade.pnl,
                    "duration": duration,
                    "opening_date": trade.opening_transaction.execution_date,
                    "closing_date": trade.closing_transaction.execution_date,
                    "commission": trade.comission,
                    "pnl_without_commission": trade.pnl_without_comission,
                }
            )

        return pd.DataFrame(data)
