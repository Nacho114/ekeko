from tqdm.autonotebook import tqdm
import pandas as pd

from ekeko.backtrader.report import Report, ReportBuilder
from ekeko.core import Ticker, Date, Stock_dfs
from ekeko.backtrader.broker import BrokerBuilder, Order, Position, Account
from ekeko.core.types import to_date

from typing import Any, Dict, Protocol
from abc import ABC, abstractmethod

class Strategy(Protocol):
    params: Dict[str, Any]

    def set_params(self, **kwargs): ...
    def evaluate(self, stock_df) -> Any: ...

class BaseStrategy(ABC):
    params: Dict[str, Any] = {}

    def set_params(self, **kwargs):
        """Generic implementation to update parameters."""
        self.params.update(kwargs)

    @abstractmethod
    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        """To be implemented by specific strategies."""
        pass

class Trader(Protocol):

    def trade(
        self,
        account: Account,
        date: Date,
        ticker: Ticker,
        signal: pd.DataFrame,
        stock_row: pd.DataFrame,
        open_positions: list[Position],
    ) -> list[Order]: ...


class Engine:

    def __init__(
        self, trader: Trader, strategy: Strategy, broker_builder: BrokerBuilder
    ):
        self.trader = trader
        self.stock_dfs = broker_builder.stock_dfs
        self.time_index = self.__get_timeindex_union(self.stock_dfs)
        self.broker = broker_builder.build(self.time_index)
        self.signal_dfs = self.__init_signal_dfs(self.stock_dfs, strategy)

    def __get_timeindex_union(self, stock_dfs: Stock_dfs) -> pd.DatetimeIndex:
        timeindex = pd.DatetimeIndex([])

        for df in stock_dfs.values():
            timeindex = timeindex.union(df.index)

        timeindex = pd.to_datetime(timeindex)
        # TODO[p=High]: What if there are different timezones, etc?
        assert isinstance(timeindex, pd.DatetimeIndex)
        return timeindex

    def __init_signal_dfs(self, stock_dfs: Stock_dfs, strategy: Strategy) -> Stock_dfs:
        signal_dfs = dict()
        for ticker, stock_df in stock_dfs.items():
            signal_df = strategy.evaluate(stock_df)
            signal_dfs[ticker] = signal_df

        return signal_dfs

    def __get_orders(self, date: Date, ticker: Ticker) -> list[Order]:
        signal_df = self.signal_dfs[ticker]
        orders = []
        if date in signal_df.index:
            signal = signal_df.loc[date]
            stock_row = self.stock_dfs[ticker].loc[date]
            open_positions = [
                p
                for p in self.broker.account.positions
                if p.transaction.order.ticker == ticker
            ]
            orders = self.trader.trade(
                self.broker.account, date, ticker, signal, stock_row, open_positions
            )
        return orders

    def run(self) -> Report:

        for date in tqdm(self.time_index, desc="Fishing ><> ~ ><>"):
            tickers = self.signal_dfs.keys()
            orders: list[Order] = []

            self.broker.update(date)

            for ticker in tickers:
                orders += self.__get_orders(date, ticker)

            before_last_date = to_date(self.time_index[-2])
            if date != before_last_date:
                self.broker.add_orders(orders)

            self.broker.add_closing_orders_for_near_expiration_positions(date)

        report_builder = ReportBuilder(
            self.broker.account, self.signal_dfs, self.stock_dfs
        )
        return report_builder.build()
