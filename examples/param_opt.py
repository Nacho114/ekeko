from pathlib import Path
import ekeko
from ekeko.backtrader.broker import (
    Account,
    BrokerBuilder,
    Order,
    OrderBuilder,
    Position,
)
from ekeko.backtrader.engine import BaseStrategy, Engine
from ekeko.backtrader.optimizer import Optimizer
from ekeko.backtrader.screener import TrivialScreener
from ekeko.data_loader import YfDataset
from ekeko.core.signal_type import ENTRY, EXIT, PLOT_COLUMNS
from ekeko.core import Ticker, Date, Number
import pandas as pd


class Strategy(BaseStrategy):
    params = {"short_window": 12, "long_window": 26, "exit_threshold": 0.05}

    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on short and long EMAs and price drop exit condition."""
        short_window = self.params["short_window"]
        long_window = self.params["long_window"]
        exit_threshold = self.params["exit_threshold"]

        # Initialize signal DataFrame
        signal = pd.DataFrame(index=stock_df.index)

        # Calculate short and long EMAs
        signal["EMA_short"] = stock_df["Close"].ewm(span=short_window, adjust=False).mean()
        signal["EMA_long"] = stock_df["Close"].ewm(span=long_window, adjust=False).mean()

        # Generate buy signals
        signal[ENTRY] = (signal["EMA_short"] > signal["EMA_long"]) & \
                        (signal["EMA_short"].shift(1) <= signal["EMA_long"].shift(1))

        # Exit condition: price drops below 5% of short EMA
        signal[EXIT] = (signal["EMA_short"] < signal["EMA_long"]) & \
                       (signal["EMA_short"].shift(1) >= signal["EMA_long"].shift(1)) | \
                       (stock_df["Close"] < signal["EMA_short"] * (1 - exit_threshold))

        # Add plot attributes
        signal.attrs[PLOT_COLUMNS] = ["EMA_short", "EMA_long"]

        return signal

class Trader:

    def trade(
        self,
        account: Account,
        date: Date,
        ticker: Ticker,
        signal: pd.DataFrame,
        stock_row: pd.DataFrame,
        open_positions: list[Position],
    ) -> list[Order]:
        _ = stock_row  # We don't use price action in Market order
        orders = []

        if signal.loc[ENTRY] and len(open_positions) == 0:
            quantity = account.get_cash(date) * 0.1 / stock_row.loc['Close']
            order = OrderBuilder(ticker, quantity).market().buy().at_date(date).build()
            orders.append(order)

        if signal.loc["exit"]:
            for p in open_positions:
                order = p.get_closing_order(date)
                orders.append(order)

        return orders


class Slippage:

    def compute(self, stock_df_row: pd.DataFrame) -> Number:
        return stock_df_row.loc["Close"]


if __name__ == "__main__":

    ekeko.config.set_num_processors(6)
    period = "2y"

    dataset = YfDataset(["CAVA"], TrivialScreener(), period)
    stock_dfs = dataset.load()

    comission = 0.01
    initial_cash = 10000

    broker_builder = BrokerBuilder(initial_cash, comission, stock_dfs, Slippage())

    # Define parameter grid
    param_grid = {
        "short_window": [10, 16],
        "long_window": [20, 30],
        "exit_threshold": [0.03, 0.05]
    }

    # Run the optimizer

    strategy = Strategy()
    optimizer = Optimizer(strategy, Trader(), stock_dfs, broker_builder, param_grid)
    report = optimizer.optimize()

    metric_fn = lambda report: report.portfolio_statistics['percentage_growth']
    grid_matrix = report.get_metric_matrix(metric_fn)
    max_param = report.get_max_metric_report(metric_fn)
    df = grid_matrix.pivot_table(index="short_window", columns="long_window", values="metric_value")

    print(grid_matrix)

    print(df)


    r = report.grid_results[0][1]
    print(r.print())
    

