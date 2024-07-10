import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt
import sys
import os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import tickers as ti  # Import custom module to get S&P 500 tickers

# Override the default pandas_datareader method to use Yahoo Finance as the data source
yf.pdr_override()

# Obtain a list of S&P 500 ticker symbols
tickers = ti.tickers_sp500()

# Replace any periods in ticker symbols with hyphens for Yahoo Finance compatibility
tickers = [item.replace('.', '-') for item in tickers]

# Define the number of years to look back for historical data
num_of_years = 10

# Calculate the start date based on the desired number of years of data
start = dt.date.today() - dt.timedelta(days=int(365.25 * num_of_years))

# Loop through each ticker symbol to retrieve historical data
for ticker in tickers:
    try:
        # Fetch historical data for the ticker from Yahoo Finance
        df = pdr.get_data_yahoo(ticker, start)

        # Define the file path to save the historical data in CSV format
        output_path = f'{ticker}.csv'
        df.to_csv(output_path)

        # Print a message indicating successful data retrieval and saving
        print(f'{ticker} historical data saved to {output_path}')

    except Exception as e:
        # Print an error message and skip to the next ticker if an error occurs
        print(f"Error fetching data for {ticker}: {e}")
        continue