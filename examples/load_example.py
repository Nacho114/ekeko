from ekeko.backtrader.screener import TrivialScreener
from ekeko.data_loader import YfDataset




period = "11y"

tickers = [ 'AAPL', 'ANNX']

screener = TrivialScreener()
dataset = YfDataset(tickers, screener, period)

# Load data for the single ticker (no caching)
stock_dfs = dataset.load()

print(stock_dfs.get('AAPL').index)
print(stock_dfs.get('ANNX').index)

