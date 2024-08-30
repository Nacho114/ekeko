import ekeko
import pandas as pd
import yfinance as yf

from ekeko.core.signal_type import ENTRY, EXIT, PLOT_COLUMNS

class Strategy:
    
    def __init__(self):
        self.short_ema = 20
        self.medium_ema = 50
        self.long_ema = 150
        self.high_window = 50
        self.exit_threshold = 0.05  # 5% below the 20-day EMA

    def evaluate(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        # Initialize signal DataFrame
        signal = pd.DataFrame(index=stock_df.index)

        # Calculate EMAs
        signal["EMA_short"] = stock_df["Close"].ewm(span=self.short_ema, adjust=False).mean()
        signal["EMA_medium"] = stock_df["Close"].ewm(span=self.medium_ema, adjust=False).mean()
        signal["EMA_long"] = stock_df["Close"].ewm(span=self.long_ema, adjust=False).mean()

        # Calculate the rolling 50-day high for 'Close' prices
        signal["50_day_high"] = stock_df["Close"].rolling(window=self.high_window).max()

        # Entry condition: Trending up + New 50-day high
        trending_up = (signal["EMA_short"] > signal["EMA_medium"]) & (signal["EMA_medium"] > signal["EMA_long"])
        new_high = stock_df["Close"] == signal["50_day_high"]
        signal[ENTRY] = trending_up & new_high

        # Exit condition: Price closes 5% below the 20-day EMA
        signal[EXIT] = stock_df["Close"] < (signal["EMA_short"] * (1 - self.exit_threshold))

        # Set columns for plotting, if needed
        signal.attrs[PLOT_COLUMNS] = ['EMA_short', 'EMA_medium', 'EMA_long', '50_day_high']

        return signal


ticker = 'NVDA'

stock_df = yf.download(ticker, period='2y')

signal = Strategy().evaluate(stock_df)

fig = ekeko.plotting.get_stock_plot_fig(stock_df, signal)
fig.show()
