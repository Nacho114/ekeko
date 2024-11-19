from typing import Protocol

from ekeko.core.types import Ticker
import pandas as pd
import yfinance as yf

from datetime import timedelta


class DataLoader(Protocol):

    def load(self, ticker: Ticker) -> pd.DataFrame | None: ...

    def process(self, stock_df: pd.DataFrame) -> pd.DataFrame: ...


class YfinanceDataLoader:

    def __init__(self, period: str):
        self.period = period

    def load(self, ticker: Ticker) -> pd.DataFrame | None:
        stock = yf.Ticker(ticker)

        stock_df = stock.history(period='max')

        if stock_df.empty:
            return None

        has_nan = stock_df.isna().any().any() # type: ignore
        if has_nan:
            print(f'{ticker} has df, but with nan values.')
            return None

        # Calculate the cutoff date based on the period
        recent_date = stock_df.index[-1]
        cutoff_date = recent_date - timedelta(days=int(self.period[:-1]) * 365)

        # Filter the DataFrame to keep rows from the cutoff date onward
        filtered_df = stock_df[stock_df.index >= cutoff_date]        

        if isinstance(filtered_df, pd.DataFrame):
            return filtered_df
    
        return None

    def process(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        return stock_df
