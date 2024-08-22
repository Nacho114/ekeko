from typing import Protocol
from ekeko.core.types import Ticker
import sys
import datetime
import yfinance as yf


class TickerScreener(Protocol):

    def passes_screen(self, ticker: Ticker) -> bool: ...


class YfinanceTickerSceener:

    def __init__(
        self, marketCapMin: int = 0, marketCapMax: int = sys.maxsize, volumeMin: int = 0, minTimeSinceFirstTrade: int = 0
    ):
        self.marketCapMin = marketCapMin
        self.marketCapMax = marketCapMax
        self.volumeMin = volumeMin
        self.minTimeSinceFirstTrade = minTimeSinceFirstTrade

    def __time_passed(self, unix_timestamp) -> int:
        date_time = datetime.datetime.fromtimestamp(unix_timestamp)

        time_delta = datetime.datetime.now() - date_time
        total_seconds = time_delta.total_seconds()

        total_months = int(total_seconds // (30.4375 * 24 * 60 * 60))

        return total_months

    def passes_screen(self, ticker: Ticker) -> bool:

        stock = yf.Ticker(ticker)
        stock_info = stock.get_info()

        keys = ["marketCap", "volume", "firstTradeDateEpochUtc"]
        for k in keys:
            if k not in stock_info:
                return False

        marketCap = stock_info["marketCap"]
        if marketCap < self.marketCapMin or marketCap > self.marketCapMax:
            return False

        volume = stock_info["volume"]
        if volume < self.volumeMin:
            return False
        
        firstTradeDate = stock_info["firstTradeDateEpochUtc"]
        numberOfMonthsSinceFirstTrade = self.__time_passed(firstTradeDate)
        if numberOfMonthsSinceFirstTrade < self.minTimeSinceFirstTrade:
            return False

        return True
