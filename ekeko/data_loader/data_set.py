from pathlib import Path
from alive_progress import alive_bar

from ekeko.backtrader.screener import TickerScreener
from ekeko.core.types import Stock_dfs, Ticker
from ekeko.data_loader.data_loader import DataLoader, YfinanceDataLoader
from ekeko.data_loader.logger import Logger
from ekeko.data_loader.ticker_processor import TickerProcessor


class Dataset:

    def __init__(
        self,
        tickers: list[Ticker],
        ticker_sceener: TickerScreener,
        data_loader: DataLoader,
    ):

        self.data_loader = data_loader
        self.ticker_processor = TickerProcessor(tickers, ticker_sceener)
        self.logger = Logger(len(tickers))

    def set_cached_tickers(self, path: Path):
        self.ticker_processor.set_cached(path)

    def load(self) -> Stock_dfs:

        tickers = self.ticker_processor.load()
        self.logger.update_tickers_that_passed_screen(len(tickers))

        stock_dfs = dict()

        with alive_bar(len(tickers), bar="squares", title="Loading dfs") as bar:
            for ticker in tickers:
                stock_df = self.data_loader.load(ticker)
                if stock_df is not None:
                    stock_df = self.data_loader.process(stock_df)
                    stock_dfs[ticker] = stock_df
                else:
                    self.logger.add_ticker_without_df(ticker)
                bar()

        self.logger.print()

        return stock_dfs


class YfDataset:

    def __init__(
        self,
        tickers: list[Ticker],
        ticker_screener: TickerScreener,
        period: str,
    ):
        self.tickers = tickers
        self.ticker_screener = ticker_screener
        self.data_loader = YfinanceDataLoader(period)
        self.dataset = Dataset(
            self.tickers, self.ticker_screener, self.data_loader
        )

    def set_cached_tickers(self, path: Path):
        self.dataset.set_cached_tickers(path)

    def load(self) -> Stock_dfs:
        return self.dataset.load()
