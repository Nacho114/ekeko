import pandas as pd

Number = float
Date = pd.Timestamp
Ticker = str


def to_number(value) -> Number:
    return float(value)


def to_date(date) -> Date:
    assert isinstance(
        date, pd.Timestamp
    ), f"Expected pd.Timestamp, but got {type(date)}"
    return date
