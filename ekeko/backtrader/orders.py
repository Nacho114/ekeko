from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from ekeko.core.types import Date, Number, Ticker

# TODO

# 1. Instrument should be a Protocol, can abstract away pd.data frame
# 2. Trader should only return relevant info (e.g. cash or account info at the day)

class OrderType:
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class OrderEntry:

    def __init__(self, ticker: Ticker):
        self.ticker = ticker 
        self.order_type = None
        self.order_action = None

    def buy(self):
        self.order_action = OrderAction.BUY

    def sell(self):
        self.order_action = OrderAction.SELL

    def market(self):
        self.order_type = OrderType.MARKET

    def submit(self):
        assert not self.order_type is None
        assert not self.order_action is None

    # Added by Broker
    def comission(self):
        ...

    #def build(self) -> Order: ...

class OrderAction(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class FillInfo:
    price: Number
    date: Date

@dataclass
class OrderInfo:
    ticker: Ticker
    action: OrderAction
    quantity: Number
    comission: Number
    order_type: OrderType
    creation_date: Date

@dataclass
class Instrument:
    ticker: Ticker

    def market_value(self, date: Date) -> Number: ...

class FilledOrder(Protocol):

    def order_info(self) -> OrderInfo: ...

    def fill_info(self) -> FillInfo: ...

    def market_value(self, date: Date) -> Number: ...

@dataclass
class DroppedOrder:
    order_info: OrderInfo
    reason: str

class Order(Protocol):

    def info(self) -> OrderInfo: ...

    def can_execute(self, date: Date) -> bool: ...

    def cost(self, date: Date) -> Number: ...

    def fill(self, date: Date) -> FilledOrder: ...


class MarketOrder:
    def info(self) -> OrderInfo: ...

    def can_execute(self, date: Date) -> bool: ...

    def cost(self, date: Date) -> Number: ...

    def fill(self, date: Date) -> FilledOrder: ...



@dataclass
class Portfolio:
    value: Number
    open_positions: Number

@dataclass 
class Trade:
    average_opining_date: Date
    closing_date: Date
    pnl: Number
    pnl_without_comission: Number
    comission: Number

@dataclass 
class Position:

    instrument: Instrument
    quantity: Number
    last_cached_mkt_value: Number

    def mkt_value_avg_price(self, date: Date): ...

    def unrealized_pnl(self, date: Date): ...

    def update(self, filled_order: FilledOrder): ...


@dataclass
class Account:
    portfolio: Number
    open_positions: dict[Ticker, Position]
    filled_orders: Number
    dropped_order: Number 

    def can_afford(self, cost: Number) -> bool:
        ...

    def add_filled_order(self, order: FilledOrder):
        ...

    def add_dropped_order(self, order: Order):
        ...

    def update(self, date: Date): ...

class OrderParser:
    @staticmethod
    def order_entry_to_order(order: OrderEntry) -> Order:
        if order.order_type == OrderType.MARKET:
            return MarketOrder()

        raise Exception(f"OrderEntry not defined for {order.order_action}")


@dataclass
class Broker:
    account: Account
    comission: Number
    pending_orders: list[Order]

    def __process_order(self, order: Order, date: Date):
            cost = order.cost(date)
            if self.account.can_afford(cost):
                filled_order = order.fill(date)
                self.account.add_filled_order(filled_order)
            else:
                self.account.add_dropped_order(order)


    def __process_pending_orders(self, date: Date):
        executable_orders: list[Order] = []
        for order in self.pending_orders:
            if order.can_execute(date):
                executable_orders.append(order)

        for order in executable_orders:
            self.__process_order(order, date)
            self.pending_orders.remove(order)


    def __submit_orders(self, orders: list[OrderEntry]):
        for order_entry in orders:
            order = OrderParser.order_entry_to_order(order_entry)
            self.pending_orders.append(order)


    def update(self, submitted_orders: list[OrderEntry], date: Date):
        self.__process_pending_orders(date)
        self.account.update(date)
        self.__submit_orders(submitted_orders)



