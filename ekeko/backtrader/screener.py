import yfinance as yf
import sys

def screener(ticker: str, marketCapMin: int = 0, marketCapMax: int = sys.maxsize, volumeMin: int = 0) -> bool:

    stock = yf.Ticker(ticker)
    stock_info = stock.get_info()


    marketCap = stock_info['marketCap']
    if marketCap < marketCapMin or marketCap > marketCapMax:
        return False

    volume = stock_info['volume']
    print(volume)
    if volume < volumeMin:
        return False

    return True
