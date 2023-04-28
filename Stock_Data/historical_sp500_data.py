# Import dependencies
import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt
import pandas as pd
import yahoo_fin.stock_info as si

# Set up Yahoo Finance API
yf.pdr_override()

# Get S&P500 tickers from Yahoo Finance
tickers = si.tickers_sp500()

# Replace any periods in ticker names with hyphens
tickers = [item.replace('.', '-') for item in tickers]

# Set number of years of historical data to retrieve
num_of_years = 10

# Calculate start date for retrieving historical data
start = dt.date.today() - dt.timedelta(days=int(365.25*num_of_years))

# Loop through tickers and retrieve historical data using Yahoo Finance API
for ticker in tickers:
    try:
        df = pdr.get_data_yahoo(ticker, start)

        # Save historical data to a CSV file
        output_path = f'{ticker}.csv'
        df.to_csv(output_path)

        print(f'{ticker} historical data saved to {output_path}')
    except:
        # If an error occurs, skip to the next ticker
        continue
