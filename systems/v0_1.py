import yfinance as yf
import backtrader as bt
import ekeko
import pandas as pd
import numpy as np

###############################
### Load Data
###############################

stock_dfs = dict()
tickers = []

ticker = "AA"
period = "2y"

stock = yf.Ticker(ticker)
stock_data = stock.history(period=period)

stock_dfs[ticker] = stock_data
tickers.append(ticker)

###############################
### Define Strategy
###############################


class SystemV1_0Strategy(bt.Strategy):
    params = dict(
        n_day_high_period=50,
        pfast=20,
        pmedium=50,
        pslow=150,
        exit_max_drop_tolerance=0.05,
    )

    def __init__(self):

        self.sell_signals = dict()
        self.buy_signals = dict()
        self.indicators = dict()

        for data in self.datas:

            ### Buy signal

            # Is new high
            max_n = bt.indicators.MaxN(data.close, period=self.params.n_day_high_period)
            is_new_high = max_n == data.close

            # Is trending
            ema_fast = bt.indicators.ExponentialMovingAverage(
                data.close, period=self.params.pfast
            )
            ema_medium = bt.indicators.ExponentialMovingAverage(
                data.close, period=self.params.pmedium
            )
            ema_slow = bt.indicators.ExponentialMovingAverage(
                data.close, period=self.params.pslow
            )

            is_trending = bt.And(ema_fast > ema_medium, ema_medium > ema_slow)

            buy_signal = bt.And(is_new_high, is_trending)
            self.buy_signals[data._name] = buy_signal

            ### sell signal

            sell_signal = data.close < ema_fast * (
                1 - self.params.exit_max_drop_tolerance
            )
            self.sell_signals[data._name] = sell_signal

            ### Save indicators

            indicators = {
                "ema_fast": ema_fast,
                "ema_medium": ema_medium,
                "ema_slow": ema_slow,
            }
            self.indicators[data._name] = indicators

    def next(self):
        for data in self.datas:
            if self.buy_signals[data._name]:
                if not self.getposition(data).size:
                    self.buy(data=data)

            if self.sell_signals[data._name]:  # Sell on odd price and on positive value
                if self.getposition(data).size:
                    self.sell(data=data)


###############################
### Backtrader add data
###############################

ekeko_cerebro = ekeko.backtrader.EkekoCerebro()

for ticker, stock_df in stock_dfs.items():
    print(ticker)
    ekeko_cerebro.adddata(stock_df, name=ticker)


###############################
### Backtrader Settings
###############################

ekeko_cerebro.cerebro.addsizer(ekeko.backtrader.FractionOfPorfolioSizer, percents=0.05)
ekeko_cerebro.cerebro.broker.setcommission(commission=0.05)
ekeko_cerebro.cerebro.addstrategy(SystemV1_0Strategy)

###############################
### Run experiment
###############################

results, analysis_results = ekeko_cerebro.run()

result_analyzer = ekeko.backtrader.EkekoResultAnalyzer(analysis_results)

result_analyzer.print()

###############################
### Plot
###############################


def to_pandas(name, line, index):
    return pd.Series(np.array(line.array), name=name, index=index)


def indicators_as_df(indicators, index):
    return [to_pandas(name, line, index) for name, line in indicators.items()]


ticker = tickers[0]
stock_df = stock_dfs[ticker]
transactions = result_analyzer.transactions[ticker]
indicators = indicators_as_df(results.indicators[ticker], stock_df.index)
fig = ekeko.viz.plot(
    stock_df, other_dfs=indicators, transactions=transactions, title=ticker
)
fig.show()
