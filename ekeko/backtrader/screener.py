from typing import Protocol
from ekeko.core.types import Ticker
import sys
import yfinance as yf


class TickerScreener(Protocol):

    def passes_screen(self, ticker: Ticker) -> bool: ...


class YfinanceTickerSceener:

    def __init__(
        self, marketCapMin: int = 0, marketCapMax: int = sys.maxsize, volumeMin: int = 0
    ):
        self.marketCapMin = marketCapMin
        self.marketCapMax = marketCapMax
        self.volumeMin = volumeMin

    def passes_screen(self, ticker: Ticker) -> bool:

        stock = yf.Ticker(ticker)
        stock_info = stock.get_info()

        marketCap = stock_info["marketCap"]
        if marketCap < self.marketCapMin or marketCap > self.marketCapMax:
            return False

        volume = stock_info["volume"]
        if volume < self.volumeMin:
            return False

        return True
