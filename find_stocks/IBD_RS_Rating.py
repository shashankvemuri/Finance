# Imports
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
import datetime
import time

# Override yfinance API
yf.pdr_override()

# Get tickers for all S&P 500 stocks and replace "." with "-" for compatibility with Yahoo Finance
sp500_tickers = si.tickers_sp500()
sp500_tickers = [ticker.replace(".", "-") for ticker in sp500_tickers]

# Define S&P 500 index
sp500_index = '^GSPC'

# Define date range for stock data
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

# Create empty list to store relative returns for each stock
relative_returns = []

# Retrieve historical price data for the S&P 500 index
sp500_df = pdr.get_data_yahoo(sp500_index, start_date, end_date)
sp500_df['Percent Change'] = sp500_df['Adj Close'].pct_change()
sp500_returns = sp500_df['Percent Change'].cumprod()
sp500_return = sp500_returns.iloc[-1]

# Iterate over all S&P 500 stocks to calculate their relative returns relative to the S&P 500
for ticker in sp500_tickers:
    # Download historical data as CSV for each stock to speed up the process
    stock_df = pdr.get_data_yahoo(ticker, start_date, end_date)
    stock_df.to_csv(f'{ticker}.csv')

    # Calculate percent change column
    stock_df['Percent Change'] = stock_df['Adj Close'].pct_change()

    # Calculate the relative return with double weight for the most recent quarter
    stock_returns = stock_df['Percent Change'].cumprod()
    stock_return = (stock_returns.iloc[-1] * 2 + stock_returns.iloc[-63]) / 3  # Double weight for the most recent quarter

    relative_return = round(stock_return / sp500_return, 2)
    relative_returns.append(relative_return)

    # Print relative return for each stock
    print(f'Ticker: {ticker}; Relative Return against S&P 500: {relative_return}\n')

    # Pause for 1 second to avoid overloading the server with requests
    time.sleep(1)

# Create dataframe with relative returns and corresponding Relative Strength (RS) rating
rs_df = pd.DataFrame(list(zip(sp500_tickers, relative_returns)), columns=['Ticker', 'Relative Return'])
rs_df['RS_Rating'] = rs_df.relative_return.rank(pct=True) * 100

# Print RS ratings for all stocks
print(rs_df)