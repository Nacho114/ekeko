from pathlib import Path
from tqdm.autonotebook import tqdm
from joblib import Parallel, delayed
import os

from ekeko.backtrader.screener import TickerScreener
from ekeko.config import config
from ekeko.core.types import Ticker


class TickerProcessor:
    def __init__(self, tickers: list[Ticker], ticker_sceener: TickerScreener):
        self.tickers = tickers
        self.ticker_screener = ticker_sceener
        self.path: None | Path = None

    def _screen_ticker(self, ticker: Ticker):
        """Checks if a ticker passes the screening criteria."""
        return ticker if self.ticker_screener.passes_screen(ticker) else None

    def __load(self) -> list[Ticker]:
        """Screen tickers using joblib for parallel processing."""
        # Use joblib's Parallel for processing tickers in parallel
        results = Parallel(n_jobs=config.num_processors)(
            delayed(self._screen_ticker)(ticker) for ticker in tqdm(self.tickers, desc="Applying screener")
        )

        # Filter out None values
        screened_tickers = [ticker for ticker in results if ticker is not None]

        return screened_tickers

    def __write(self, tickers: list[Ticker], path: Path):
        """Write screened tickers to a file."""
        with open(path, "w") as file:
            for ticker in tickers:
                file.write(ticker + "\n")

    def __load_from_cache(self, path: Path) -> list[Ticker]:
        """Load tickers from cache or screen and cache them if not available."""
        if os.path.exists(path):
            print("Loading ticker data from cache")
            with open(path, "r") as file:
                screened_tickers = [line.strip() for line in file]
        else:
            screened_tickers = self.__load()
            self.__write(screened_tickers, path)

        return screened_tickers

    def set_cached(self, path: Path):
        """Set the cache path for storing screened tickers."""
        tickers_info = f"num_tickers_{len(self.tickers)}_"
        self.path = path / Path(tickers_info + self.ticker_screener.info() + ".txt")

    def load(self) -> list[Ticker]:
        """Load tickers, using cache if available."""
        if self.path:
            tickers = self.__load_from_cache(self.path)
        else:
            tickers = self.__load()

        return tickers

