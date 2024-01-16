# Imports
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import datetime
import time
import sys
import os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import tickers as ti

# Override yfinance API for pandas datareader
yf.pdr_override()

# Retrieve S&P 500 tickers and format for Yahoo Finance
sp500_tickers = ti.tickers_sp500()
sp500_tickers = [ticker.replace(".", "-") for ticker in sp500_tickers]

# Set S&P 500 index ticker
sp500_index = '^GSPC'

# Define date range for stock data
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

# Initialize list for storing relative stock returns
relative_returns = []

# Fetch and process S&P 500 historical data
sp500_df = pdr.get_data_yahoo(sp500_index, start_date, end_date)
sp500_df['Percent Change'] = sp500_df['Adj Close'].pct_change()
sp500_cumulative_return = sp500_df['Percent Change'].cumprod().iloc[-1]

# Compute relative returns for each S&P 500 stock
for ticker in sp500_tickers:
    try:
        # Download stock data
        stock_df = pdr.get_data_yahoo(ticker, start_date, end_date)
        stock_df['Percent Change'] = stock_df['Adj Close'].pct_change()

        # Calculate cumulative return with added emphasis on recent quarter
        stock_cumulative_return = (stock_df['Percent Change'].cumprod().iloc[-1] * 2 + 
                                   stock_df['Percent Change'].cumprod().iloc[-63]) / 3

        # Calculate relative return compared to S&P 500
        relative_return = round(stock_cumulative_return / sp500_cumulative_return, 2)
        relative_returns.append(relative_return)

        print(f'Ticker: {ticker}; Relative Return against S&P 500: {relative_return}')
        time.sleep(1)  # Pause to prevent overloading server
    except Exception as e:
        print(f'Error processing {ticker}: {e}')

# Create dataframe with relative returns and RS ratings
rs_df = pd.DataFrame({'Ticker': sp500_tickers, 'Relative Return': relative_returns})
rs_df['RS_Rating'] = rs_df['Relative Return'].rank(pct=True) * 100
print(rs_df)