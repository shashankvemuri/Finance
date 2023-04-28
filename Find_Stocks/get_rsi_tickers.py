# Import Dependencies
import requests
import datetime
import talib
from pandas_datareader import DataReader
import pickle
import bs4 as bs
import time
import pandas as pd
import progressbar

# Get dates for the past year
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

# Load list of S&P 500 tickers from file
tickers = pd.read_pickle('spxTickers.pickle')

oversold_tickers = []
overbought_tickers = []

# Loop through each ticker
for i, ticker in zip(progressbar.progressbar(range(len(tickers))), tickers):
    try:
        # Download data for the ticker
        data = DataReader(ticker, 'yahoo', start_date, end_date)

        # Calculate the RSI
        data["rsi"] = talib.RSI(data["Close"])

        # Get the last 14 RSI values and calculate the mean
        values = data["rsi"].tail(14)
        mean_rsi = values.mean()

        # Print the RSI value for the ticker
        print(f'\n{ticker} has an RSI value of {round(mean_rsi, 2)}')
        time.sleep(1)

        # Add the ticker to the appropriate list based on its RSI value
        if mean_rsi <= 30:
            oversold_tickers.append(ticker)
        elif mean_rsi >= 70:
            overbought_tickers.append(ticker)

    except Exception as e:
        print(f'Error processing {ticker}: {e}')

# Print the list of oversold and overbought tickers
print(f'Oversold tickers: {oversold_tickers}')
print(f'Overbought tickers: {overbought_tickers}')