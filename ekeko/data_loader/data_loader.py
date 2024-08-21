from typing import Protocol

from ekeko.core.types import Ticker
import pandas as pd
import yfinance as yf


class DataLoader(Protocol):

    def load(self, ticker: Ticker) -> pd.DataFrame: ...

    def process(self, stock_df: pd.DataFrame) -> pd.DataFrame: ...


class YfinanceDataLoader:

    def __init__(self, period: str):
        self.period = period

    def load(self, ticker: Ticker) -> pd.DataFrame:
        stock = yf.Ticker(ticker)
        period = self.period
        stock_df = stock.history(period=period)

        return stock_df

    def process(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        return stock_df
