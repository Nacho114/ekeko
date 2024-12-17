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
from ekeko.backtrader.screener import YfinanceTickerSceener, TrivialScreener
from ekeko.data_loader import YfDataset

from ekeko.core import Ticker, Date, Number

import pandas as pd

import pandas as pd
import numpy as np

class Strategy:

    def __init__(self):
        self.short_ema = 20
        self.medium_ema = 50
        self.long_ema = 200
        self.tema_window = 17  # Customizable window for TEMA
        self.high_window = 50
        self.max_volatility_window = 50  # Window for max ATR calculation
        self.min_volatility_window = 50  # Window for min ATR calculation
        self.exit_threshold = 0.05  # 5% below the 20-day EMA
        self.max_significance_threshold = 2  # Significance multiplier for max threshold
        self.min_significance_threshold = 2  # Significance multiplier for min threshold

    def get_threshold_for_max(self, volatility, mean_price):
        """Returns the threshold that needs to be crossed to register a significant upper bound."""
        return mean_price + self.max_significance_threshold * volatility

    def get_threshold_for_min(self, volatility, mean_price):
        """Returns the threshold that needs to be crossed to register a significant lower bound."""
        return mean_price - self.min_significance_threshold * volatility

    def get_mean_price(self, prices):
        """Calculates the mean price from a list or array of prices."""
        return np.mean(prices)

    def tema(self, series, window):
        """Calculates the Triple Exponential Moving Average (TEMA)."""
        ema1 = series.ewm(span=window, adjust=False).mean()
        ema2 = ema1.ewm(span=window, adjust=False).mean()
        ema3 = ema2.ewm(span=window, adjust=False).mean()
        return 3 * (ema1 - ema2) + ema3

    def calculate_gradients(self, series):
        """Calculates the gradient of a series (e.g., upper/lower thresholds)."""
        return np.gradient(series)

    def calculate_roc(self, data, period=10):
        """
        Calculate the Rate of Change (ROC) for a given period.

        Parameters:
        - data: A pandas Series of numeric values (e.g., stock prices).
        - period: The number of periods for the ROC calculation (e.g., 10 days).

        Returns:
        - A pandas Series with the ROC values.
        """
        roc = ((data - data.shift(period)) / data.shift(period)) * 100
        return roc

    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        # Initialize signal DataFrame
        signal = pd.DataFrame(index=stock_df.index)

        # Calculate EMAs (Comment out any if not needed)
        signal["EMA_short"] = stock_df["Close"].ewm(span=self.short_ema, adjust=False).mean()
        signal["EMA_medium"] = stock_df["Close"].ewm(span=self.medium_ema, adjust=False).mean()
        signal["EMA_long"] = stock_df["Close"].ewm(span=self.long_ema, adjust=False).mean()

        # Calculate TEMA
        signal["TEMA"] = self.tema(stock_df["Close"], self.tema_window)

        # Calculate True Range (TR)
        stock_df['Prev_Close'] = stock_df['Close'].shift(1)
        stock_df['High_Low'] = stock_df['High'] - stock_df['Low']
        stock_df['High_Close'] = abs(stock_df['High'] - stock_df['Prev_Close'])
        stock_df['Low_Close'] = abs(stock_df['Low'] - stock_df['Prev_Close'])
        stock_df['True_Range'] = stock_df[['High_Low', 'High_Close', 'Low_Close']].max(axis=1)

        # Calculate Average True Range (ATR) for maxima and minima
        signal['ATR_max'] = stock_df['True_Range'].rolling(window=self.max_volatility_window).mean()
        signal['ATR_min'] = stock_df['True_Range'].rolling(window=self.min_volatility_window).mean()

        # Calculate mean prices for highs and lows
        signal['Mean_High_Price'] = stock_df['High'].rolling(window=self.max_volatility_window).mean()
        signal['Mean_Low_Price'] = stock_df['Low'].rolling(window=self.min_volatility_window).mean()

        # Calculate upper and lower thresholds
        signal['Upper_Threshold'] = self.get_threshold_for_max(signal['ATR_max'], signal['Mean_High_Price'])
        signal['Lower_Threshold'] = self.get_threshold_for_min(signal['ATR_min'], signal['Mean_Low_Price'])

        # Calculate gradients of thresholds (Comment out if not needed)
        signal['Upper_Threshold_Gradient'] = self.calculate_gradients(signal['Upper_Threshold'])*100
        signal['Lower_Threshold_Gradient'] = self.calculate_gradients(signal['Lower_Threshold'])*100

        #calculate long ema gradient
        signal['EMA_long_Gradient'] = self.calculate_gradients(signal['EMA_long'])*100

        #ema medim gradient
        signal['EMA_medium_Gradient'] = self.calculate_gradients(signal['EMA_medium'])*100

        #ema short gradient
        signal['EMA_short_Gradient'] = self.calculate_gradients(signal['EMA_short'])*100

        #calculate 11 day roc
        signal['ROC_Upper_Threshold'] = self.calculate_roc(data=signal['Upper_Threshold'], period=20)
        signal['ROC_Lower_Threshold'] = self.calculate_roc(data=signal['Lower_Threshold'], period=20)

        #ROC price 20
        signal['ROC_Close'] = self.calculate_roc(data=stock_df['Close'], period=20)

        #roc price 60
        signal['ROC_Close_60'] = self.calculate_roc(data=stock_df['Close'], period=60)


        # Calculate the rolling 50-day high for 'Close' prices
        signal["50_day_high"] = stock_df["Close"].rolling(window=self.high_window).max()

        # Entry condition: Trending up + New 50-day high (Original)
        #trending_up = (signal['Lower_Threshold_Gradient'] > 0) & (signal['Upper_Threshold_Gradient'] > 0) & (signal['EMA_short'] > signal['EMA_long'])
        tema_above_lower_threshold = (signal["TEMA"] > signal["Lower_Threshold"]) & (signal["TEMA"].shift(1) <= signal["Lower_Threshold"].shift(1))
        #trending_up = signal['Lower_Threshold_Gradient'] > -10
        signal[ENTRY] = tema_above_lower_threshold

        # New Exit Condition with two components
        # 1. If TEMA < Upper Threshold, exit if TEMA crosses below Lower Threshold
        exit_below_upper_cross_lower = (signal["TEMA"] < signal["Lower_Threshold"]) & (signal["TEMA"].shift(1) >= signal["Lower_Threshold"].shift(1))
        #(signal["TEMA"] < signal["Upper_Threshold"]) &
        # 2. If TEMA > Upper Threshold, exit if TEMA crosses below Upper Threshold
        exit_above_upper_cross_upper = (signal["TEMA"] < signal["Upper_Threshold"]) & (signal["TEMA"].shift(1) > signal["Upper_Threshold"].shift(1))
        #exit_tema_cross_ema = (signal["TEMA"].shift(3) > signal["EMA_short"].shift(3)) & (signal["TEMA"] < signal["EMA_short"])
        #signal[EXIT] = exit_tema_cross_ema
        #combined_exit_signal = exit_below_upper_cross_lower | exit_above_upper_cross_upper
        #(signal["TEMA"] > signal["Upper_Threshold"]) &
        # Combined Exit Signal
        signal[EXIT] = exit_below_upper_cross_lower | exit_above_upper_cross_upper

        # Set columns for plotting, if needed
        signal.attrs[PLOT_COLUMNS] = ['EMA_short', 'EMA_medium', 'EMA_long', '50_day_high', 'TEMA', 'Upper_Threshold', 'Lower_Threshold', 'Upper_Threshold_Gradient', 'Lower_Threshold_Gradient',] #'ROC_Upper_Threshold', 'ROC_Lower_Threshold','EMA_long_Gradient', 'ROC_Close', 'ROC_Close_60', 'ATR_max', 'ATR_min', 'EMA_short_Gradient', 'EMA_medium_Gradient']

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

        if signal.loc["entry"] and len(open_positions) == 0:

            # Note, if price tomorrow is different, then the quantity might not
            # be appropriate


            quantity = account.get_min_of_cash_and_value(date) * 0.95 / stock_row.loc['Close']
            cost = quantity * stock_row.loc['Close']

            if account.get_cash(date) > cost:
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


# Configure ekeko processors
ekeko.config.set_num_processors(4)

# Set criteria for filtering tickers (if relevant for single ticker)
marketCapMin = int(0.1 * 1e0)
marketCapMax = int(500 * 1e25)
volumeMin = int(2 * 1e0)
minTimeSinceFirstTrade = 12
period = "2y"

tickers = ['ZC=F', 'HO=F']

# Initialize screener and dataset with a single ticker
#screener = YfinanceTickerSceener(marketCapMin, marketCapMax, volumeMin, minTimeSinceFirstTrade)

screener = TrivialScreener()
dataset = YfDataset(tickers, screener, period)

# Load data for the single ticker (no caching)
stock_dfs = dataset.load()



# Define the commission rate and initial cash amount
commission = 0.01
initial_cash = 100000

# If stock_dfs is a dictionary (e.g., stock_dfs = {'AAPL': <DataFrame>}), access the single ticker's DataFrame
# Replace 'AAPL' with the actual ticker symbol used in tickers[0]
#single_stock_df = stock_dfs[tickers[0]] if isinstance(stock_dfs, dict) else stock_dfs

# Wrap single_stock_df in a dictionary if it's not already one
#stock_dfs_dict = {tickers[0]: single_stock_df} if not isinstance(stock_dfs, dict) else stock_dfs

# Initialize the broker with the single ticker's data dictionary
broker_builder = BrokerBuilder(initial_cash, commission, stock_dfs, Slippage())
engine = Engine(Trader(), Strategy(), broker_builder)

# Run the engine and generate the report
report = engine.run()

# Add benchmarks
#report.add_ticker_to_benchmark('QQQ', period)
report.add_sceener_index_to_benchmark(stock_dfs)
report.print()

