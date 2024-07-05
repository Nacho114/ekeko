import ekeko

def test_stooq_loader():

    root_dir = '/home/nacho/code/ekeko/data/stooq/daily/us/nasdaq stocks'
    stooq_data = ekeko.dataloader.read_us_stooq_data(root_dir)

    ticker = next(iter(stooq_data.keys()))

    file_path = stooq_data[ticker]
    df = ekeko.dataloader.stooq_to_df(file_path)

    print(len(stooq_data))
    print(df.head())
