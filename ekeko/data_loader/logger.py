from ekeko.core.types import Ticker

class Logger:

    def __init__(self, total_number_of_tickers: int):
        self.total_number_of_tickers = total_number_of_tickers
        self.tickers_that_passed_screen = total_number_of_tickers
        self.tickers_without_df : list[Ticker] = []

    def update_tickers_that_passed_screen(self, num: int):
        self.tickers_that_passed_screen = num

    def add_ticker_without_df(self, ticker: Ticker):
        self.tickers_without_df.append(ticker)

    def print(self):
        have_df = self.tickers_that_passed_screen - len(self.tickers_without_df)
        print(f'> Out of {self.total_number_of_tickers} tickers: {self.tickers_that_passed_screen} passed the screener, and from those {have_df} have df.')
