import glob
import pandas as pd
import os
from pathlib import Path

def read_us_stooq_data(root_dir: str) -> dict[str, Path]:
    """
    Reads all stooq files recursively within a given `root_dir`. It expects
    files to be named AA.us.txt.
    
    Parameters: 
    root_dir (str): Root directory of stooq folder
   
    Returns:
    dict[str, Path]: Dict of ticker to filepath
    """

    # Ensure the root directory ends with a separator
    # otherwise **/*.txt returns an empty list
    if not root_dir.endswith(os.path.sep):
        root_dir += os.path.sep

    stocks: dict[str, Path] = {}

    for filename in glob.iglob(root_dir + '**/*.txt', recursive=True):
        filepath = Path(filename)
        name = filepath.stem
        
        # Note stooq data is usually of the form AA.us.txt
        # we want to make sure this is the case
        name = name.split('.')
        assert len(name) == 2
        assert name[1] == 'us'

        ticker = name[0]
        stocks[ticker] = filepath

    return stocks


def stooq_to_df(file_path: Path) -> pd.DataFrame:
    """
    Converts a stooq data file into a pandas df
    
    Parameters: 
    file_path (str): Path of file
   
    Returns:
    pd.DataFrame: df of OHLCV data
    """
    # Read the CSV content from the file into a DataFrame
    df: pd.DataFrame = pd.read_csv(file_path, delimiter=',')  # assuming tab-separated values

    # Rename columns to match yfinance DataFrame
    df.rename(columns={
        '<DATE>': 'Date',
        '<OPEN>': 'Open',
        '<HIGH>': 'High',
        '<LOW>': 'Low',
        '<CLOSE>': 'Close',
        '<VOL>': 'Volume'
    }, inplace=True)

    # Convert the 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')

    # Set the timezone to America/New_York
    df['Date'] = df['Date'].dt.tz_localize('America/New_York')

    # Set the 'Date' column as the index
    df.set_index('Date', inplace=True)

    _df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    if not isinstance(_df, pd.DataFrame):
        raise TypeError(f"Expected object of type {pd.DataFrame.__name__}, but got {type(_df).__name__}")

    df = _df

    # Extract the ticker symbol from the file name (e.g., 'gps.us.txt' -> 'gps')
    file_name = os.path.basename(file_path)
    ticker = file_name.split('.')[0]

    # Set the ticker as the index name
    df.index.name = ticker

    return df
