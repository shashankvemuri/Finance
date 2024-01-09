# Import Dependencies
import datetime
from pandas_datareader import data as pdr
import sys
import os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import ta_functions as ta
import tickers as ti

# Get dates for the past year
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

# Load list of S&P 500 tickers from file
tickers = ti.tickers_sp500()

# Lists to hold overbought and oversold tickers
oversold_tickers = []
overbought_tickers = []

# Download data for the tickers
sp500_data = pdr.get_data_yahoo(tickers, start_date, end_date)['Adj Close']

# Loop through each ticker
for ticker in tickers:
    try:
        # New dataframe for the ticker
        data = sp500_data[[ticker]].copy()

        # Calculate the RSI
        data["rsi"] = ta.RSI(data[ticker], timeperiod=14)

        # Get the last 14 RSI values and calculate the mean
        values = data["rsi"].tail(14)
        mean_rsi = values.mean()

        # Print the RSI value for the ticker
        print(f'{ticker} has an RSI value of {round(mean_rsi, 2)}')

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