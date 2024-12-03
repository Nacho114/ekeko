from ekeko.core import to_number, Ticker, Number, Date, Stock_dfs
from enum import Enum
from dataclasses import dataclass
import pandas as pd

from typing import Protocol

from ekeko.core.types import to_date


class OrderAction(Enum):
    BUY = "BUY"
    SELL = "SELL"


class InstrumentType(Enum):
    STOCK = "STOCK"


class OrderType(Enum):
    MARKET = "Market"


@dataclass
class Order:
    instrument_type: InstrumentType
    ticker: Ticker
    quantity: Number
    order_type: OrderType
    order_action: OrderAction
    date: Date

    @property
    def is_buy(self) -> bool:
        return self.order_action == OrderAction.BUY

    @property
    def is_sell(self) -> bool:
        return self.order_action == OrderAction.SELL

    @property
    def is_stock(self) -> bool:
        return self.instrument_type == InstrumentType.STOCK

    @property
    def is_market(self) -> bool:
        return self.order_type == OrderType.MARKET


class OrderBuilder:

    def __init__(self, ticker: Ticker, quantity: float):
        self.ticker: Ticker = ticker
        self.quantity: float = quantity
        self.order_type: OrderType | None = None
        self.instrument_type: InstrumentType = InstrumentType.STOCK
        self.order_action: OrderAction | None = None
        self.date: Date | None = None

    # Error in colab: ImportError: cannot import name 'Self' from 'typing', so cannot use type for return
    def market(self):
        self.order_type = OrderType.MARKET
        return self

    def buy(self):
        self.order_action = OrderAction.BUY
        return self

    def sell(self):
        self.order_action = OrderAction.SELL
        return self

    def at_date(self, date: Date):
        self.date = date
        return self

    def build(self) -> Order:
        if self.order_type == None:
            raise Exception("OrderType not defined")
        if self.instrument_type == None:
            raise Exception("InstrumentType not defined")
        if self.order_action == None:
            raise Exception("OrderAction not defined")
        if self.date == None:
            raise Exception("date not defined")
        if self.date == None:
            raise Exception("date not defined")

        return Order(
            self.instrument_type,
            self.ticker,
            self.quantity,
            self.order_type,
            self.order_action,
            self.date,
        )


@dataclass
class Transaction:
    order: Order
    comission: Number
    comission_rate: Number
    execution_price: Number
    execution_date: Date
    cost: Number

    def __str__(self) -> str:
        return f"Transaction(order={self.order}, execution_price={self.execution_price}, execution_date={self.execution_date})"


class Slippage(Protocol):

    def compute(self, stock_df_row: pd.DataFrame) -> Number: ...


class SlippageOnClose:

    def compute(self, stock_df_row: pd.DataFrame) -> Number:
        return to_number(stock_df_row.loc["Close"])


@dataclass
class StockDFWrapper:
    stock_dfs: Stock_dfs
    slippage: Slippage

    def has_record(self, order: Order, date: Date) -> bool:
        return date in self.stock_dfs[order.ticker].index

    def get_value_at_close(self, order: Order, date: Date) -> Number:
        value = self.stock_dfs[order.ticker]["Close"][date]
        return to_number(value)

    def get_with_slippage(self, order: Order, date: Date) -> Number:
        stock_df_row = self.stock_dfs[order.ticker].loc[date]
        return self.slippage.compute(stock_df_row)


class OrderProcessor:

    def __init__(
        self,
        stock_dfs: Stock_dfs,
        comission_rate: Number,
        slippage: Slippage,
    ):
        self.stock_dfs = StockDFWrapper(stock_dfs, slippage)
        self.comission_rate = comission_rate

    def process_order(self, order: Order, date: Date) -> Transaction:
        if order.is_stock:
            cost, execution_price, comission = self.__transaction_cost(order, date)
            return Transaction(order, comission, self.comission_rate,execution_price, date, cost)

        raise Exception(f"Not defined for {type(order.instrument_type)}")

    def can_execute_order(self, order: Order, date: Date) -> bool:
        if order.is_stock:
            if self.stock_dfs.has_record(order, date):
                if order.is_market:
                    return True
            else:
                return False

        raise Exception(f"Not defined for {type(order.instrument_type)}")

    def __transaction_cost(self, order: Order, date: Date) -> tuple[Number, Number, Number]:
        execution_price = self.stock_dfs.get_with_slippage(order, date)
        execution_price = to_number(execution_price)
        sign = to_number(-1.0 if order.is_buy else 1.0)
        comission = execution_price * order.quantity * self.comission_rate
        cost = (sign * execution_price * order.quantity) - comission
        return cost, execution_price, comission

    def value_at(self, order: Order, date: Date) -> Number:
        if order.is_stock:
            stock_value = self.stock_dfs.get_value_at_close(order, date)
            value = stock_value * order.quantity
            if order.is_buy:
                return value
            if order.is_sell:
                return -value

        raise Exception(f"Not defined for {type(order.order_type)}")

    def has_record(self, order: Order, date: Date) -> bool:
        return self.stock_dfs.has_record(order, date)

@dataclass
class Trade:
    opening_transaction: Transaction
    closing_transaction: Transaction
    comission: Number
    pnl: Number
    pnl_without_comission: Number
    relative_gain: Number

    def __str__(self) -> str:
        return f"Trade pnl {self.pnl}"


@dataclass
class Position:
    transaction: Transaction

    def is_closed_by(self, other_t: Transaction) -> bool:
        if self.transaction.order.is_stock and other_t.order.is_stock:
            orders_have_same_ticker = (
                self.transaction.order.ticker == other_t.order.ticker
            )
            same_quantity = self.transaction.order.quantity == other_t.order.quantity
            opposite_actions = (
                self.transaction.order.order_action != other_t.order.order_action
            )
            return orders_have_same_ticker and same_quantity and opposite_actions

        return False

    def close(self, closing_transaction: Transaction) -> Trade:
        assert self.is_closed_by(closing_transaction)

        if self.transaction.order.is_stock and closing_transaction.order.is_stock:
            opening_transaction = self.transaction
            comission = opening_transaction.comission + closing_transaction.comission
            pnl = (
                closing_transaction.execution_price
                - opening_transaction.execution_price
            )
            is_short_trade = closing_transaction.order.is_buy
            if is_short_trade:
                pnl *= -1
            pnl_without_comission = pnl * self.transaction.order.quantity
            pnl = pnl_without_comission - comission

            if opening_transaction.order.is_buy:
                relative_gain = closing_transaction.execution_price / opening_transaction.execution_price - 1
            else:
                relative_gain = opening_transaction.execution_price / closing_transaction.execution_price - 1

            # Calculate commission as a proportion of the opening price
            commission_rate = opening_transaction.comission_rate

            # Adjust relative gain to account for commissions
            # +1 for the equation and +1 since relative gain is normalized to 0
            commission_adjustment = commission_rate * (1 + 1 + relative_gain) 
            relative_gain = relative_gain - commission_adjustment

            return Trade(
                opening_transaction,
                closing_transaction,
                comission,
                pnl,
                pnl_without_comission,
                relative_gain
            )
                

        raise Exception(f"Not defined for {type(self.transaction.order.order_type)}")

    def get_closing_order(self, date: Date) -> Order:
        if self.transaction.order.is_stock:
            instrument = self.transaction.order.instrument_type
            ticker = self.transaction.order.ticker
            quantity = self.transaction.order.quantity
            action = (
                OrderAction.SELL if self.transaction.order.is_buy else OrderAction.BUY
            )
            return Order(instrument, ticker, quantity, OrderType.MARKET, action, date)

        raise Exception(f"Not defined for {type(self.transaction.order.order_type)}")

    def __str__(self) -> str:
        return f"Position(transaction={self.transaction})"


@dataclass
class Account:

    def __init__(self, initial_cash: Number, time_index: pd.DatetimeIndex):
        self.value_df = pd.DataFrame(
            index=time_index, columns=["cash", "open_position"]  # type: ignore
        )
        # Set the initial cash balance for the first index
        self.value_df.iloc[0, self.value_df.columns.get_loc("cash")] = initial_cash
        self.value_df.iloc[0, self.value_df.columns.get_loc("open_position")] = 0.0

        self.positions: list[Position] = []
        self.trades: list[Trade] = []
        self.transactions: list[Transaction] = []
        self.dropped_transaction: list[Transaction] = []
        self.tickers: set[Ticker] = set()
        self.cached_df_values: dict[Ticker, Number] = {}

    def get_cash(self, date: Date) -> Number:
        cash = to_number(self.value_df.loc[date, "cash"])
        return cash

    def get_value(self, date: Date) -> Number:
        cash = self.get_cash(date)
        open_position_value = self.value_df.loc[date, "open_position"]
        value = cash + open_position_value
        return value

    def get_min_of_cash_and_value(self, date: Date) -> Number:
        cash = self.get_cash(date)
        value = self.get_value(date)
        return min(cash, value)

    def add_transaction(self, transaction: Transaction):
        if self.value_df.loc[transaction.execution_date, "cash"] + transaction.cost < 0:
            self.dropped_transaction.append(transaction)
            return

        self.value_df.loc[transaction.execution_date, "cash"] += transaction.cost

        self.transactions.append(transaction)

        position_to_be_closed = None
        for position in self.positions:
            if position.is_closed_by(transaction):
                position_to_be_closed = position

        if position_to_be_closed:
            self.positions.remove(position_to_be_closed)
            trade = position_to_be_closed.close(transaction)
            self.trades.append(trade)
        else:
            self.positions.append(Position(transaction))

    def update_cash_and_open_value(self, order_processor: OrderProcessor, date: Date):
        self.__update_cash(date)
        self.__update_open_position(order_processor, date)

    def __update_cash(self, date: Date):
        idx = self.value_df.index.get_loc(date)
        assert isinstance(idx, int)
        if idx < len(self.value_df.index) - 1:
            current_cash_value = self.value_df.loc[date, "cash"]
            next_date = self.value_df.index[idx + 1]
            self.value_df.loc[next_date, "cash"] = current_cash_value

    def __update_open_position(self, order_processor: OrderProcessor, date: Date):
        value_at_date = 0.0
        for p in self.positions:
            ticker = p.transaction.order.ticker
            if order_processor.has_record(p.transaction.order, date):
                value = order_processor.value_at(p.transaction.order, date)
                self.cached_df_values[ticker] = value
            else:
                value = self.cached_df_values[ticker]

            value_at_date += value
        self.value_df.loc[date, "open_position"] = value_at_date


@dataclass
class Broker:
    def __init__(
        self,
        account: Account,
        comission: Number,
        stock_dfs: Stock_dfs,
        slippage: Slippage | None = None,
    ):
        self.account = account
        self.comission = comission
        self.order_queue: list[Order] = []
        if not slippage:
            slippage = SlippageOnClose()
        self.order_processor = OrderProcessor(stock_dfs, comission, slippage)
        self.stock_dfs = stock_dfs

    def __process_queue(self, date: Date):
        executable_orders = []
        for order in self.order_queue:
            if self.order_processor.can_execute_order(order, date):
                executable_orders.append(order)


        for order in executable_orders:
            transaction = self.order_processor.process_order(order, date)
            self.account.add_transaction(transaction)
            self.order_queue.remove(order)

    def __update_account(self, date: Date):
        self.account.update_cash_and_open_value(self.order_processor, date)

    def add_orders(self, orders: list[Order]):
        self.order_queue += orders

    def add_closing_orders_for_near_expiration_positions(self, date: Date):
        closing_orders: list[Order] = []

        for position in self.account.positions:
            ticker = position.transaction.order.ticker
            stock_data = self.stock_dfs.get(ticker)

            # Proceed only if we have data for the ticker
            if stock_data is not None and date in stock_data.index:
                current_index = stock_data.index.get_loc(date)
                is_second_to_last_day = current_index == len(stock_data.index) - 2

                # If the stock is nearing its last trading day, create a closing order
                if is_second_to_last_day:
                    closing_order = position.get_closing_order(date)
                    closing_orders.append(closing_order)

        self.order_queue += closing_orders


    def update(self, date: Date):
        self.__process_queue(date)
        self.__update_account(date)

@dataclass
class BrokerBuilder:
    initial_cash: Number
    comission: Number
    stock_dfs: Stock_dfs
    slippage: Slippage | None = None

    def build(self, time_index) -> Broker:

        if not self.slippage:
            self.slippage = SlippageOnClose()

        account = Account(self.initial_cash, time_index)
        return Broker(account, self.comission, self.stock_dfs, self.slippage)
