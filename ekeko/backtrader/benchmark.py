import pandas as pd

from ekeko.core.types import Number, Stock_dfs, Ticker
from ekeko.data_loader.data_loader import YfinanceDataLoader


class ScreenedIndex:

    def __init__(self, stock_dfs: Stock_dfs):
        normalized_dfs = {}
        for ticker, df in stock_dfs.items():
            normalized_df = df["Close"] / df["Close"].iloc[0]
            normalized_dfs[ticker] = normalized_df

        combined_normalized = pd.concat(normalized_dfs.values(), axis=1)

        average_normalized_close = combined_normalized.mean(axis=1)
        average_normalized_close.name = "Screener index"  # type: ignore

        self.average_returns = average_normalized_close

    def get_average_returns(self) -> pd.DataFrame:
        return self.average_returns  # type: ignore


class Benchmark:

    def __init__(self):
        self.returns: dict[Ticker, Number] = {}
        self.dfs: dict[Ticker, pd.DataFrame] = {}

    def is_not_empty(self) -> bool:
        return len(self.returns) != 0

    def __with_df(self, df: pd.DataFrame):
        first_price = df.iloc[0]
        last_price = df.iloc[-1]

        returns = last_price / first_price

        df_close = df / df.iloc[0]

        self.returns[df.name] = returns
        self.dfs[df.name] = df_close

    def with_ticker(self, ticker: Ticker, period: str):
        loader = YfinanceDataLoader(period)
        stock_df = loader.load(ticker)
        assert isinstance(stock_df, pd.DataFrame)
        stock_df = stock_df["Close"]
        stock_df.name = ticker
        self.__with_df(stock_df)

    def with_stock_dfs(self, dfs: Stock_dfs):
        index = ScreenedIndex(dfs)
        self.__with_df(index.get_average_returns())

    def get_benchmark_dfs(self) -> list[pd.DataFrame]:
        return list(self.dfs.values())

    def print(self, strategy_return: float):
        print(f"{'Us':<16} {strategy_return:.4f}")
        for ticker, returns in self.returns.items():
            # Check if 'ticker' is a string
            if isinstance(ticker, str):
                ticker_str = f"{ticker:<16}"
            else:
                ticker_str = str(ticker)

            # Check if 'returns' is a number (int or float)
            if isinstance(returns, (int, float)):
                returns_str = f"{returns:.4f}"
            else:
                returns_str = str(returns)

            print(f"{ticker_str} {returns_str}")
