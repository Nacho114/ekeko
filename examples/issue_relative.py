from pathlib import Path
import ekeko
from ekeko.core.signal_type import ENTRY, EXIT, PLOT_COLUMNS
from ekeko.backtrader.broker import (
    Account,
    BrokerBuilder,
    Order,
    OrderBuilder,
    Position,
)

from ekeko.backtrader.engine import Engine
from ekeko.backtrader.screener import TrivialScreener
from ekeko.data_loader import YfDataset

from ekeko.core import Ticker, Date, Number

import pandas as pd


class Strategy:
    def __init__(self):
        self.short_window = 15
        self.long_window = 55

    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        # Initialize signal DataFrame
        signal = pd.DataFrame(index=stock_df.index)

        # Calculate short and long EMAs and add to signal DataFrame
        signal["EMA_short"] = (
            stock_df["Close"].ewm(span=self.short_window, adjust=False).mean()
        )
        signal["EMA_long"] = (
            stock_df["Close"].ewm(span=self.long_window, adjust=False).mean()
        )

        # Generate buy and sell signals#swapped < signs
        signal[ENTRY] = (signal["EMA_short"] < signal["EMA_long"]) & (
            signal["EMA_short"].shift(1) >= signal["EMA_long"].shift(1)
        )
        signal[EXIT] = (signal["EMA_short"] > signal["EMA_long"]) & (
            signal["EMA_short"].shift(1) <= signal["EMA_long"].shift(1)
        )

        signal.attrs[PLOT_COLUMNS] = ['EMA_short', 'EMA_long']


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

            # Note, if price tomorrow is different, then the quantity might not
            # be appropriate


            quantity = account.get_min_of_cash_and_value(date) * 0.05 / stock_row.loc['Close']
            cost = quantity * stock_row.loc['Close']

            if account.get_cash(date) > cost:
                order = OrderBuilder(ticker, quantity).market().buy().at_date(date).build()

                orders.append(order)

        if signal.loc[EXIT]:
            for p in open_positions:
                order = p.get_closing_order(date)
                orders.append(order)

        return orders


class Slippage:

    def compute(self, stock_df_row: pd.DataFrame) -> Number:
        return stock_df_row.loc["Close"]
# Configure ekeko processors


ekeko.config.set_num_processors(4)

period = "2y"

# tickers = ['FWRD', 'NRGV', 'VOXX', 'IAS', 'FTCI', 'EAF', 'IHRT', 'CHTR', 'JOBY', 'REPL', 'LVS', 'DBX', 'AMBP', 'SFIX', 'NAPA', 'HNRG', 'PLTK', 'ATUS', 'LBRDK', 'MP', 'ERAS', 'COGT', 'LFST', 'AY', 'CRK', 'EDR', 'EPD', 'UA', 'ADT', 'BYD', 'ENLC', 'KVYO', 'BLCO', 'DNB', 'PL', 'SWI', 'UAA', 'SLGN', 'GOOG', 'GOOGL', 'TEAM', 'SMG', 'OLO', 'GSAT', 'SNDR', 'BRK-B', 'WOW', 'MPLX', 'RSG', 'RCM', 'DRVN', 'SCCO', 'WRB', 'LBTYK', 'H', 'NWSA', 'ATSG', 'GRAB', 'GLBE', 'ALTR', 'TW', 'SUM', 'CLMT', 'CWAN', 'TRTX', 'GFL', 'LYV', 'NWS', 'LBTYA', 'KIND', 'NDAQ', 'WMT', 'WEAV', 'FOXA', 'OUT', 'FOX', 'JWN', 'ORGO', 'MNDY', 'CRBG', 'CPNG', 'RXT', 'GBTG', 'CG', 'TMUS', 'ORCL', 'SEM', 'HCP', 'PLG', 'CART', 'DRS', 'BGC', 'ALKT', 'SRAD', 'ULCC', 'BAM', 'CCL', 'APLD', 'RL', 'MS', 'NVEI', 'NU', 'ALHC', 'OKLO', 'ACLX', 'BX', 'DASH', 'Z', 'PEGA', 'DELL', 'ZG', 'PAYO', 'PGRU', 'IOT', 'ONON', 'VERX', 'WRBY', 'APO', 'AMRX', 'AVPT', 'SGMT', 'BFLY', 'DOCS', 'PPC', 'QNCX', 'BV', 'KGS', 'LMND', 'TRUP', 'GRND', 'GLUE', 'JEF', 'SLNO', 'CLBT', 'CNTA', 'KKR', 'DESP', 'MMYT', 'CIFR', 'RVLV', 'BZFD', 'GAU', 'AUR', 'ANNX', 'MTZ', 'CMPO', 'PRQR', 'BTDR', 'SPOT', 'TOST', 'TMQ', 'BVS', 'GATO', 'NN', 'CLOV', 'CENX', 'SPRY', 'VERA', 'BYRN', 'HOOD', 'QUBT', 'APLT', 'HYLN', 'RAIL', 'ASPI', 'RKLB', 'CDXC', 'HNST', 'EWTX', 'CRVS', 'RCAT', 'WULF', 'APP', 'WGS', 'VIK', 'WAY', 'RDDT', 'SERV', 'ULS', 'TEM', 'TBBB', 'AS', 'ALAB', 'BTSG', 'CGON', 'RBRK', 'OS', 'NNE']
tickers = [ 'KIND', 'ANNX']
# tickers = tickers[:10]

screener = TrivialScreener()
dataset = YfDataset(tickers, screener, period)

# Load data for the single ticker (no caching)
stock_dfs = dataset.load()

# Define the commission rate and initial cash amount
commission = 0.01
initial_cash = 10000

# Initialize the broker with the single ticker's data dictionary
broker_builder = BrokerBuilder(initial_cash, commission, stock_dfs, Slippage())
engine = Engine(Trader(), Strategy(), broker_builder)

# Run the engine and generate the report
report = engine.run()

# Add benchmarks
report.add_ticker_to_benchmark('QQQ', period)
report.add_sceener_index_to_benchmark(stock_dfs)
report.print()

print(engine.broker.account.positions)

# report.plot_stock(tickers[0])

print(report.transactions)
