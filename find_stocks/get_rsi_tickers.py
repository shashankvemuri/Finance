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

# Load list of S&P 500 tickers from tickers module
tickers = ti.tickers_sp500()

# Initialize lists for overbought and oversold tickers
oversold_tickers = []
overbought_tickers = []

# Retrieve adjusted close prices for the tickers
sp500_data = pdr.get_data_yahoo(tickers, start_date, end_date)['Adj Close']

# Analyze each ticker for RSI
for ticker in tickers:
    try:
        # Create a new DataFrame for the ticker
        data = sp500_data[[ticker]].copy()

        # Calculate the RSI for the ticker
        data["rsi"] = ta.RSI(data[ticker], timeperiod=14)

        # Calculate the mean of the last 14 RSI values
        mean_rsi = data["rsi"].tail(14).mean()

        # Print the RSI value
        print(f'{ticker} has an RSI value of {round(mean_rsi, 2)}')

        # Classify the ticker based on its RSI value
        if mean_rsi <= 30:
            oversold_tickers.append(ticker)
        elif mean_rsi >= 70:
            overbought_tickers.append(ticker)

    except Exception as e:
        print(f'Error processing {ticker}: {e}')

# Output the lists of oversold and overbought tickers
print(f'Oversold tickers: {oversold_tickers}')
print(f'Overbought tickers: {overbought_tickers}')