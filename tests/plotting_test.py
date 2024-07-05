import ekeko
import pandas as pd
import numpy as np

def create_fake_data(prices):
    num_days = len(prices)
    dates = pd.date_range(start='2022-01-01', periods=num_days, freq='D')
    df = pd.DataFrame(index=dates)
    df['Open'] = prices
    df['High'] = prices
    df['Low'] = prices
    df['Close'] = prices
    df['Volume'] = np.random.rand( num_days, 1)
    return df

def test_ekeko_viz_plot():

    x = np.linspace(0, 1000, 100)
    cosine = np.cos(x*np.pi/180) + 10

    stock_df = create_fake_data(cosine)

    other_dfs = [stock_df['Open']]

    dates = pd.to_datetime([
        '2022-02-01',
        '2022-02-15',
        '2022-03-03',
        '2022-03-20',
        '2022-04-01'
    ])

    sizes = [1, -1, 1, -1, 1]

    prices = stock_df['Open'][dates.strftime('%Y-%m-%d')]

    transactions = pd.DataFrame({
        'size': sizes,
        'price': prices,
    }, index=dates)

    buys = transactions[transactions['size'] > 0]
    sells = transactions[transactions['size'] < 0]

    fig = ekeko.viz.plot(stock_df, other_dfs=other_dfs, transactions=transactions)

    assert fig is not None
