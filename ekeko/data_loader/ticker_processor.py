from pathlib import Path
from tqdm.autonotebook import tqdm
from multiprocess import Pool

from ekeko.backtrader.screener import TickerScreener
from ekeko.config import config
import os

from ekeko.core.types import Ticker


class TickerProcessor:

    def __init__(self, tickers: list[Ticker], ticker_sceener: TickerScreener):
        self.tickers = tickers
        self.ticker_screener = ticker_sceener
        self.path: None | Path = None

    def __screen_ticker(self, ticker: Ticker):
        return ticker if self.ticker_screener.passes_screen(ticker) else None

    def __load(self) -> list[Ticker]:

        with Pool(processes=config.num_processors) as pool:
            results = list(
                tqdm(
                    pool.imap(self.__screen_ticker, self.tickers),
                    total=len(self.tickers),
                    desc="Applying screener",
                )
            )

        screened_tickers = [ticker for ticker in results if ticker is not None]

        return screened_tickers

    def __write(self, tickers: list[Ticker], path: Path):
        with open(path, "w") as file:
            for ticker in tickers:
                file.write(ticker + "\n")

    def __load_from_cache(self, path: Path) -> list[Ticker]:
        screened_tickers = []
        if os.path.exists(path):
            print("Loading ticker data from cache")
            with open(path, "r") as file:
                screened_tickers = [line.strip() for line in file]
        else:
            screened_tickers = self.__load()
            self.__write(screened_tickers, path)

        return screened_tickers

    def set_cached(self, path: Path):
        tickers_info = f"num_tickers_{len(self.tickers)}_"
        self.path = path / Path(tickers_info + self.ticker_screener.info() + ".txt")

    def load(self) -> list[Ticker]:
        if self.path:
            tickers = self.__load_from_cache(self.path)
        else:
            tickers = self.__load()

        return tickers
