from pathlib import Path
from alive_progress import alive_bar

from ekeko.backtrader.screener import TickerScreener
from ekeko.core.types import Stock_dfs
from ekeko.data_loader.data_loader import DataLoader, YfinanceDataLoader
from ekeko.data_loader.ticker_loader import TickerLoader, TickerReader


class Dataset:

    def __init__(
        self,
        ticker_loader: TickerLoader,
        ticker_sceener: TickerScreener,
        data_loader: DataLoader,
    ):

        self.data_loader = data_loader
        self.ticker_reader = TickerReader(ticker_loader, ticker_sceener)

    def set_cached_tickers(self, path: Path):
        self.ticker_reader.set_cached(path)

    def load(self) -> Stock_dfs:

        tickers = self.ticker_reader.load()

        stock_dfs = dict()

        with alive_bar(len(tickers), bar="squares", title="Loading dfs") as bar:
            for ticker in tickers:
                stock_df = self.data_loader.load(ticker)
                if len(stock_df.index) != 0:
                    stock_df = self.data_loader.process(stock_df)
                    stock_dfs[ticker] = stock_df
                bar()

        return stock_dfs


class YfDataset:

    def __init__(
        self,
        ticker_loader: TickerLoader,
        ticker_screener: TickerScreener,
        period: str,
    ):
        self.ticker_loader = ticker_loader
        self.ticker_screener = ticker_screener
        self.data_loader = YfinanceDataLoader(period)
        self.dataset = Dataset(
            self.ticker_loader, self.ticker_screener, self.data_loader
        )

    def set_cached_tickers(self, path: Path):
        self.dataset.set_cached_tickers(path)

    def load(self) -> Stock_dfs:
        return self.dataset.load()
