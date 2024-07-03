import ekeko
import backtrader as bt
import pandas as pd

###############################
### Create fake data
###############################

# Create fake data
def create_fake_data(prices):
    num_days = len(prices)
    dates = pd.date_range(start='2022-01-01', periods=num_days, freq='D')
    df = pd.DataFrame(index=dates)
    df['Open'] = prices
    df['High'] = prices
    df['Low'] = prices
    df['Close'] = prices
    df['Volume'] = 1000
    return df

stock_dfs = {
    "STOCK_1": create_fake_data([2, 4, 6, -500, 3, 5]),
    "STOCK_2": create_fake_data([2, 4, 3, 1])
}

###############################
### Define Strategy
###############################

class EvenOddStrategy(bt.Strategy):
    def __init__(self):
        self.order = None

    def next(self):
        for data in self.datas:
            if data.close[0] % 2 == 0:  # Buy on even price
                if not self.getposition(data).size:
                    self.order = self.buy(data=data)

            if data.close[0] % 2 != 0 and data.close[0] > 0:  # Sell on odd price and on positive value
                if self.getposition(data).size:
                    self.order = self.sell(data=data)

###############################
### Run experiment
###############################

ekeko_cerebro = ekeko.backtrader.EkekoCerebro()
ekeko_cerebro.cerebro.broker.setcash(2000.0)

for ticker, stock_df in stock_dfs.items():
    ekeko_cerebro.adddata(stock_df, name=ticker)

ekeko_cerebro.addstrategy(EvenOddStrategy)

results, analysis_results = ekeko_cerebro.run()

result_analyzer = ekeko.backtrader.EkekoResultAnalyzer(analysis_results)

result_analyzer.print()
