import pandas as pd
from dataclasses import dataclass

from ekeko.backtrader.broker import Account, OrderAction, Trade, Transaction
from ekeko.core.types import Date, Ticker

import random


class ReportBuilder:

    def __init__(self, account: Account, signal_dfs: dict[Ticker, pd.DataFrame]):

        self.account = account
        self.signal_dfs = signal_dfs

    def build(self):

        transactions = self.__transactions_to_df(self.account.transactions)
        trades = self.__trades_to_df(self.account.trades)
        trade_statistics = self.__compute_trades_statistics(trades)
        portfolio = self.__fill_in_portfolio(self.account.value_df)
        portfolio_statistics = self.__compute_portfolio_statistics(portfolio)

        report = Report(
            transactions,
            trades, 
            trade_statistics,
            portfolio,
            portfolio_statistics,
            self.signal_dfs
        )

        return report


    def __transactions_to_df(self, transactions: list[Transaction]) -> pd.DataFrame:
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

    def __trades_to_df(self, trades: list[Trade]) -> pd.DataFrame:
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

    def __compute_trades_statistics(self, trades: pd.DataFrame) -> dict[str, float]:

        trade_statistics = {}

        trade_statistics['total_trades'] = len(trades)
        trade_statistics['avg_pnl'] = trades['pnl'].mean()
        trade_statistics['avg_duration'] = trades['duration'].mean()

        positive_pnl = trades[trades['pnl'] > 0]['pnl']
        trade_statistics['avg_positive_pnl'] = positive_pnl.mean()

        negative_pnl = trades[trades['pnl'] < 0]['pnl']
        trade_statistics['avg_negative_pnl'] = negative_pnl.mean()
        trade_statistics['num_positive'] = len(positive_pnl)
        trade_statistics['num_negative'] = len(negative_pnl)
        trade_statistics['pain_gain_ratio'] = trade_statistics['avg_positive_pnl'] / abs(trade_statistics['avg_negative_pnl'])

        return trade_statistics


    def __fill_in_portfolio(self, portfolio: pd.DataFrame) -> pd.DataFrame:

        portfolio['value'] = portfolio['cash'] + portfolio['open_position']
        portfolio['normalized_value'] = portfolio['value'] / portfolio.iloc[0]['cash']

        return portfolio


    def __compute_portfolio_statistics(self, portfolio: pd.DataFrame) -> dict[str, float]:
        last_row = portfolio.iloc[-1]

        last_row_dict = last_row.to_dict()

        initial_cash = portfolio.iloc[0]['cash']
        final_value = last_row['value']
        percentage_growth = ((final_value - initial_cash) / initial_cash) * 100
        last_row_dict['percentage_growth'] = percentage_growth

        return last_row_dict


## TODO:

# 1. Get Indicators
# 2. Get transactions for plotting

def print_random_quote():
    quotes = [
        "when an inner situation is not made conscious, it happens outside, as Fate. - CJ",
        "There is always something trending",
        "Nature does not hurry, yet everything is accomplished. - Lao Tzu",
        "Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment. - Buddha",
        "Silence is the language of God, all else is poor translation. - Rumi",
        "He who knows others is wise; he who knows himself is enlightened. - Lao Tzu",
        "The quieter you become, the more you can hear. - Ram Dass",
        "Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself. - Rumi",
        "Peace comes from within. Do not seek it without. - Buddha",
    ]
    print(random.choice(quotes))

# Call the function to print a random quote



@dataclass
class Report:
    transactions: pd.DataFrame
    trades: pd.DataFrame
    trades_statistics: dict[str, float]
    portfolio: pd.DataFrame
    portfolio_statistics: dict[str, float]
    signal_dfs: dict[Ticker, pd.DataFrame]

    def __print_dict(self, dicto: dict[str, float]):
        for key, value in dicto.items():
            print(f"{key:20} {value:.4f}")

    def __print_header(self, header: str):
        print()
        print('='*6, ' ', header, ' ', '='*6)
        print()

    def print(self):
        self.__print_header("Report")
        print_random_quote()
        self.__print_header("Transactions")

        print(self.transactions)
        self.__print_header("Trades")
        trades = self.trades.sort_values(by='pnl', ascending=False)
        print(trades)
        self.__print_header("Trade stats")
        self.__print_dict(self.trades_statistics)
        self.__print_header("Portfolio stats")
        self.__print_dict(self.portfolio_statistics)
        print()

    def transactions_for_plotting(self, ticker: Ticker) -> pd.DataFrame:
        # Filter the dataframe for the given ticker
        df = self.transactions
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

    def get_indicators_for_plotting(self, ticker: Ticker) -> list[pd.Series]:
        indicator = []
        signal = self.signal_dfs[ticker]
        for column in signal.columns:
            if column not in ["buy", "sell"]:
                df = pd.DataFrame({column: signal[column]})
                df = signal[column].copy()
                indicator.append(df)

        return indicator
