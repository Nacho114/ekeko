import ekeko
import yfinance as yf

def test_screener():

    ticker = 'AA'

    stock = yf.Ticker(ticker)

    stock_info = stock.get_info()

    marketCap = stock_info['marketCap']
    volume = stock_info['volume']

    print(f'Market cap {marketCap}')
    print(f'Volume {marketCap}')

    passes_screener = ekeko.backtrader.screener(ticker)
    print(passes_screener)
    import sys
    print(sys.maxsize)

    assert passes_screener
