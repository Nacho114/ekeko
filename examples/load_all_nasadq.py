from alive_progress import alive_bar
from ekeko.backtrader.screener import YfinanceTickerSceener
from ekeko.core.types import Ticker
from ekeko.data_loader import YfDataset
from pathlib import Path

import requests

def fetch_nasdaq_tickers(url):
    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Split the text content by lines
        lines = response.text.splitlines()

        # Initialize an empty list to hold tickers
        tickers = []

        # Iterate through lines and extract tickers
        for line in lines:
            # Skip lines that do not start with a valid ticker (assumed to be valid if it has a length of more than 1 character)
            if line and not line.startswith('Symbol'):
                # Split the line by tab character
                parts = line.split('|')
                if len(parts) > 1:
                    ticker = parts[0].strip()
                    tickers.append(ticker)

        return tickers
    else:
        # Handle the case where the request was not successful
        raise Exception(f"Failed to fetch data from {url}. Status code: {response.status_code}")

# URL of the NASDAQ file
url = 'http://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt'

# Fetch and print the list of tickers
tickers = fetch_nasdaq_tickers(url)

cache_path = 'examples/cached'

import yfinance as yf

def has_ticker_info(ticker):

    stock = yf.Ticker(ticker)
    stock_info = stock.get_info()
    
    keys = ["marketCap", "volume", "firstTradeDateEpochUtc"]
    for k in keys:
        if k not in stock_info:
            # print(f'{ticker} has no {k}')
            return False

    return True



counter = 0

with alive_bar(len(tickers), bar="halloween", title="...") as bar:
    for ticker in tickers:
        if not has_ticker_info(ticker):
            counter += 1
        bar()

print(f'{len(tickers)}: Without info: {counter}')
# class TestScreener:
#
#     def passes_screen(self, ticker: Ticker) -> bool: 
#         return True
#
#     def info(self) -> str: 
#         return "test_screener"
#
#
#
# marketCapMin = int(2*1e9)
# marketCapMax = int(20*1e9)
# volumeMin = int(2*1e5)
# minTimeSinceFirstTrade = 12
#
# # screener = YfinanceTickerSceener()
# screener = TestScreener()
# dataset = YfDataset(tickers, screener, period="2y")
# dataset.set_cached_tickers(Path(cache_path))
# stock_dfs = dataset.load()
# print(stock_dfs.keys())
