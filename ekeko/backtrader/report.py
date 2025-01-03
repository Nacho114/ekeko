import pandas as pd
from dataclasses import dataclass

from ekeko.backtrader.benchmark import Benchmark
from ekeko.backtrader.broker import Account, OrderAction, Trade, Transaction
from ekeko.core.types import Date, Ticker, Stock_dfs

import ekeko.fun as fun
from ekeko.plotting.plotting import get_stock_plot_fig, get_equity_curve_fig


class ReportBuilder:

    def __init__(self, account: Account, signal_dfs: Stock_dfs, stock_dfs: Stock_dfs):

        self.account = account
        self.signal_dfs = signal_dfs
        self.stock_dfs = stock_dfs

    def build(self):

        transactions = self.__transactions_to_df(self.account.transactions)
        trades = self.__trades_to_df(self.account.trades)
        trade_statistics = self.__compute_trades_statistics(trades)
        relative_trade_statistics = self.__compute_relative_trade_statistics(trades)
        portfolio = self.__fill_in_portfolio(self.account.value_df)
        portfolio_statistics = self.__compute_portfolio_statistics(portfolio)

        report = Report(
            transactions,
            trades,
            trade_statistics,
            relative_trade_statistics,
            portfolio,
            portfolio_statistics,
            self.stock_dfs,
            self.signal_dfs,
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
            duration = get_duration(
                trade.opening_transaction.execution_date,
                trade.closing_transaction.execution_date,
            )
            data.append(
                {
                    "ticker": trade.opening_transaction.order.ticker,
                    "pnl": trade.pnl,
                    "relative_gain": trade.relative_gain,
                    "duration": duration,
                    "opening_date": trade.opening_transaction.execution_date,
                    "closing_date": trade.closing_transaction.execution_date,
                    "commission": trade.comission,
                    "pnl_without_commission": trade.pnl_without_comission,
                }
            )

        return pd.DataFrame(data)

    def __compute_trades_statistics(self, trades: pd.DataFrame) -> dict[str, float]:
        if trades.empty:
            return {}

        trade_statistics = {}

        trade_statistics["total_trades"] = len(trades)
        trade_statistics["avg_pnl"] = trades["pnl"].mean()
        trade_statistics["median_pnl"] = trades["pnl"].median()
        trade_statistics["avg_duration"] = trades["duration"].mean()

        positive_pnl = trades[trades["pnl"] > 0]["pnl"]
        trade_statistics["avg_positive_pnl"] = positive_pnl.mean()

        negative_pnl = trades[trades["pnl"] < 0]["pnl"]
        trade_statistics["avg_negative_pnl"] = negative_pnl.mean()
        trade_statistics["num_positive"] = len(positive_pnl)
        trade_statistics["num_negative"] = len(negative_pnl)

        if trade_statistics["avg_negative_pnl"] != 0:
            trade_statistics["gain_pain_ratio"] = trade_statistics[
                "avg_positive_pnl"
            ] / abs(trade_statistics["avg_negative_pnl"])
        else:
            trade_statistics["gain_pain_ratio"] = None

        if len(negative_pnl) != 0 and trade_statistics["gain_pain_ratio"]:
            pos_to_neg_pnl_ratio = len(positive_pnl) / len(negative_pnl)
            trade_statistics["avg_gain_pain_ratio"] = (
                trade_statistics["gain_pain_ratio"] * pos_to_neg_pnl_ratio
            )
        else:
            trade_statistics["avg_gain_pain_ratio"] = None

        return trade_statistics

    def __compute_relative_trade_statistics(
        self, trades: pd.DataFrame
    ) -> dict[str, float]:
        if trades.empty:
            return {}

        relative_trade_statistics = {}

        relative_trade_statistics["total_trades"] = len(trades)
        relative_trade_statistics["avg_relative_gain"] = trades["relative_gain"].mean()
        relative_trade_statistics["median_relative_gain"] = trades[
            "relative_gain"
        ].median()
        relative_trade_statistics["avg_duration"] = trades["duration"].mean()

        positive_gain = trades[trades["relative_gain"] > 0]["relative_gain"]
        relative_trade_statistics["avg_positive_gain"] = positive_gain.mean()

        negative_gain = trades[trades["relative_gain"] < 0]["relative_gain"]
        relative_trade_statistics["avg_negative_gain"] = negative_gain.mean()
        relative_trade_statistics["num_positive"] = len(positive_gain)
        relative_trade_statistics["num_negative"] = len(negative_gain)

        if relative_trade_statistics["avg_negative_gain"] != 0:
            relative_trade_statistics["gain_pain_ratio"] = relative_trade_statistics[
                "avg_positive_gain"
            ] / abs(relative_trade_statistics["avg_negative_gain"])
        else:
            relative_trade_statistics["gain_pain_ratio"] = None

        if len(negative_gain) != 0 and relative_trade_statistics["gain_pain_ratio"]:
            pos_to_neg_gain_ratio = len(positive_gain) / len(negative_gain)
            relative_trade_statistics["avg_gain_pain_ratio"] = (
                relative_trade_statistics["gain_pain_ratio"] * pos_to_neg_gain_ratio
            )
        else:
            relative_trade_statistics["avg_gain_pain_ratio"] = None

        return relative_trade_statistics

    def __fill_in_portfolio(self, portfolio: pd.DataFrame) -> pd.DataFrame:
        portfolio["value"] = portfolio["cash"] + portfolio["open_position"]
        portfolio["normalized_value"] = portfolio["value"] / portfolio.iloc[0]["cash"]
        portfolio["cummax"] = portfolio["normalized_value"].cummax()

        return portfolio

    def __add_drawdown_statistics(
        self, stats: dict[str, float], portfolio: pd.DataFrame
    ):
        drawdown = portfolio["cummax"] - portfolio["normalized_value"]
        normalized_drawdown = drawdown / portfolio["cummax"]
        max_drawdown = normalized_drawdown.max()
        stats["max_drawdown"] = max_drawdown

        temp = drawdown[drawdown == 0]
        periods = temp.index[1:].to_pydatetime() - temp.index[:-1].to_pydatetime()

        max_drawdown_duration = 0
        if len(periods) != 0:
            max_drawdown_duration = periods.max()

        stats["max_drawdown_duration"] = max_drawdown_duration

    def __compute_portfolio_statistics(
        self, portfolio: pd.DataFrame
    ) -> dict[str, float]:
        last_row = portfolio.iloc[-1]

        last_row_dict = last_row.to_dict()

        initial_cash = portfolio.iloc[0]["cash"]
        final_value = last_row["value"]
        percentage_growth = ((final_value - initial_cash) / initial_cash) * 100
        last_row_dict["percentage_growth"] = percentage_growth

        del last_row_dict["cummax"]

        self.__add_drawdown_statistics(last_row_dict, portfolio)

        return last_row_dict


@dataclass
class Report:
    transactions: pd.DataFrame
    trades: pd.DataFrame
    trades_statistics: dict[str, float]
    relative_trades_statistics: dict[str, float]
    portfolio: pd.DataFrame
    portfolio_statistics: dict[str, float]
    stock_dfs: Stock_dfs
    signal_dfs: Stock_dfs
    benchmark: Benchmark = Benchmark()

    def __print_dict(self, dicto: dict[str, float]):
        for key, value in dicto.items():
            if isinstance(value, float):
                print(f"{key:<20} {value:.4f}")
            else:
                print(f"{key:<20} {value}")

    def __print_header(self, header: str):
        print()
        print("=" * 6, " ", header, " ", "=" * 6)
        print()

    def __print_benchmark(self):
        if self.benchmark.is_not_empty():
            self.__print_header("Benchmarks")
            returns = self.portfolio_statistics["normalized_value"]
            self.benchmark.print(returns)

    def add_ticker_to_benchmark(self, ticker: Ticker, period: str):
        self.benchmark.with_ticker(ticker, period)

    def add_sceener_index_to_benchmark(self, stock_dfs: Stock_dfs):
        self.benchmark.with_stock_dfs(stock_dfs)

    def print(self):
        pd.set_option("display.max_columns", None)
        self.__print_header("Report")

        fun.print_random_quote()

        self.__print_header("Trade stats")
        self.__print_dict(self.trades_statistics)
        self.__print_header("Relative trade stats")
        self.__print_dict(self.relative_trades_statistics)
        self.__print_header("Portfolio stats")
        self.__print_dict(self.portfolio_statistics)
        self.__print_benchmark()
        print()

    def print_transactions_and_trades(self):
        pd.set_option("display.max_columns", None)
        self.__print_header("Transactions")

        print(self.transactions)
        self.__print_header("Trades")
        if not self.trades.empty:
            trades = self.trades.sort_values(by="pnl", ascending=False)
            print(trades)
        else:
            print("No trades done.")
        print()

    def transactions_for_plotting(self, ticker: Ticker) -> pd.DataFrame | None:
        # Filter the dataframe for the given ticker
        df = self.transactions

        if self.transactions.empty:
            return None

        ticker_df = df[df["ticker"] == ticker].copy()

        if ticker_df.empty:
            return None

        # Convert date to datetime and set as index
        ticker_df["date"] = pd.to_datetime(ticker_df["date"])
        ticker_df.set_index("date", inplace=True)

        # Create value column (negative for buy, positive for sell)
        ticker_df["value"] = -ticker_df["size"] * ticker_df["execution_price"]

        # Select and reorder columns
        result_df = ticker_df[["size", "execution_price", "value", "commission"]]
        result_df.columns = ["size", "price", "value", "commission"]  # type: ignore

        assert isinstance(result_df, pd.DataFrame)

        return result_df

    def plot_stock(self, ticker: Ticker):
        transactions = self.transactions_for_plotting(ticker)
        signal = self.signal_dfs[ticker]
        stock_df = self.stock_dfs[ticker]
        fig = get_stock_plot_fig(
            stock_df, signal=signal, transactions=transactions, title=ticker
        )
        fig.show()

    def plot_equity_curve(self):
        fig = get_equity_curve_fig(self.portfolio, self.benchmark.get_benchmark_dfs())
        fig.show()
