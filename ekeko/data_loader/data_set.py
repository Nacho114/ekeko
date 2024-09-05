from pathlib import Path
from tqdm.autonotebook import tqdm
from multiprocess import Pool
from ekeko.config import config

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

    def __process_ticker(self, ticker):
        stock_df = self.data_loader.load(ticker)
        if stock_df is not None:
            stock_df = self.data_loader.process(stock_df)
            return ticker, stock_df
        else:
            return ticker, None

    def load(self) -> Stock_dfs:

        tickers = self.ticker_processor.load()
        self.logger.update_tickers_that_passed_screen(len(tickers))

        stock_dfs = dict()

        with Pool(processes=config.num_processors) as pool:
            results = list(
                tqdm(
                    pool.imap(self.__process_ticker, tickers),
                    total=len(tickers),
                    desc="Loading dfs",
                )
            )

        for ticker, df in results:
            if df is not None:
                stock_dfs[ticker] = df
            else:
                self.logger.add_ticker_without_df(ticker)

        self.logger.print()

        return stock_dfs


class YfDataset:

    def __init__(
        self,
        tickers: list[Ticker],
        ticker_screener: TickerScreener,
        period: str | list[str],
    ):
        self.tickers = tickers
        self.ticker_screener = ticker_screener
        self.data_loader = YfinanceDataLoader(period)
        self.dataset = Dataset(self.tickers, self.ticker_screener, self.data_loader)

    def set_cached_tickers(self, path: Path):
        self.dataset.set_cached_tickers(path)

    def load(self) -> Stock_dfs:
        return self.dataset.load()
