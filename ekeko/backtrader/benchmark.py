import yfinance as yf


def get_returns(ticker: str, period: str = "2y") -> float:
    spy_data = yf.download(ticker, period=period)

    first_price = spy_data["Close"].iloc[0]  # First day's closing price
    last_price = spy_data["Close"].iloc[-1]  # Last day's closing price

    returns = last_price / first_price

    return returns
