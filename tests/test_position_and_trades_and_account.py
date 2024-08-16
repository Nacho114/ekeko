import ekeko
from ekeko.backtrader.broker import (
    Account,
    Order,
    InstrumentType,
    OrderType,
    OrderAction,
    Broker,
)
import pandas as pd


def test_broker_buy():  # Test cases
    data_a = {
        "Close": [1, 4, 2, 3, 6, 7],
    }
    index = pd.to_datetime(
        [
            "2023-08-03",
            "2023-08-04",
            "2023-08-05",
            "2023-08-07",
            "2023-08-08",
            "2023-08-09",
        ]
    )
    stock_df_a = pd.DataFrame(data_a, index=index)
    ticker_a = "Aurora"

    data_b = {
        "Close": [1, 4, 2, 2, 6, 7],
    }
    index_b = pd.to_datetime(
        [
            "2023-08-03",
            "2023-08-04",
            "2023-08-05",
            "2023-08-07",
            "2023-08-08",
            "2023-08-09",
        ]
    )
    stock_df_b = pd.DataFrame(data_b, index=index_b)
    ticker_b = "Beyblade"

    stock_dfs = {ticker_a: stock_df_a, ticker_b: stock_df_b}

    comission = 0.01
    initial_cash = 1000
    quantity = 10

    account = Account(initial_cash, index)
    broker = Broker(account, comission, stock_dfs)

    for date in index:
        orders = []
        for ticker, stock_df in stock_dfs.items():
            if stock_df.loc[date, "Close"] == 1:
                order = Order(
                    InstrumentType.STOCK,
                    ticker,
                    quantity,
                    OrderType.MARKET,
                    OrderAction.BUY,
                    date,
                )
                orders.append(order)

            if stock_df.loc[date, "Close"] == 3:
                for p in broker.account.positions:
                    if p.transaction.order.ticker == ticker:
                        order = p.get_closing_order(date)
                        orders.append(order)

        broker.update(orders, date)

    # print(broker.account.value_df)
    # eval.display()
