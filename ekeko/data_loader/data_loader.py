from typing import Protocol

from ekeko.core.types import Ticker
import pandas as pd
import yfinance as yf


class DataLoader(Protocol):

    def load(self, ticker: Ticker) -> pd.DataFrame | None: ...

    def process(self, stock_df: pd.DataFrame) -> pd.DataFrame: ...


class YfinanceDataLoader:

    def __init__(self, period: str | list[str]):
        if isinstance(period, str):
            period = [period]
        self.period = period

    def load(self, ticker: Ticker) -> pd.DataFrame | None:
        stock = yf.Ticker(ticker)

        for p in self.period:
            stock_df = stock.history(period=p)

            if stock_df.empty:
                return None

            return stock_df

    def process(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        return stock_df
