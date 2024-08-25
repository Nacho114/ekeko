from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from ekeko.core.types import Date, Number, Ticker

class OrderAction(Enum):
    BUY = "BUY"
    SELL = "SELL"

class Order(Protocol):

    def ticker(self) -> Ticker: ...

    def quantity(self) -> Number: ...

    def action(self) -> OrderAction: ...

    def comission(self) -> Number: ...

    def can_execute_at(self, date: Date) -> bool: ...

    def value_at(self, date: Date) -> Number: ...

    def get_closing_order(self) -> 'Order': ...

    def is_closed_by(self, other: 'Order') -> bool: ...

class MarketOrder:

    def __init__(self, ticker: Ticker, action: OrderAction):
        self.__ticker = ticker
        self.__action = action

    def ticker(self) -> Ticker: 
        return self.__ticker

    def quantity(self) -> Number:
        return -1

    def comission(self) -> Number:
        return -1

    def action(self) -> OrderAction: 
        return self.__action

    def can_execute_at(self, date: Date) -> bool: 
        return True

    def value_at(self, date: Date) -> Number: 
        return -1
    
    def get_closing_order(self) -> 'MarketOrder':
        opposite_action = OrderAction.BUY if self.action() == OrderAction.SELL else OrderAction.SELL
        return MarketOrder(self.__ticker, opposite_action)

    def is_closed_by(self, other: Order) -> bool: 
        if not isinstance(other, MarketOrder):
            return False
        have_same_quantity = self.quantity() == other.quantity()
        have_opposite_action = self.action() != other.action()
        return have_same_quantity and have_opposite_action





def test(order: Order):
    print(order.ticker())

order = MarketOrder('hello', OrderAction.BUY)
test(order)



