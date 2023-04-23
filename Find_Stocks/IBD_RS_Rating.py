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

# Create empty list to store returns multiples for each stock
returns_multiples = []

# Retrieve historical price data for the S&P 500 index
sp500_df = pdr.get_data_yahoo(sp500_index, start_date, end_date)
sp500_df['Percent Change'] = sp500_df['Adj Close'].pct_change()
sp500_return = (sp500_df['Percent Change'] + 1).cumprod()[-1]

# Iterate over all S&P 500 stocks to calculate their returns multiple relative to the S&P 500
for ticker in sp500_tickers:
    # Download historical data as CSV for each stock to speed up the process
    stock_df = pdr.get_data_yahoo(ticker, start_date, end_date)
    stock_df.to_csv(f'{ticker}.csv')

    # Calculate returns multiple
    stock_df['Percent Change'] = stock_df['Adj Close'].pct_change()
    stock_return = (stock_df['Percent Change'] + 1).cumprod()[-1]
    returns_multiple = round((stock_return / sp500_return), 2)
    returns_multiples.extend([returns_multiple])

    # Print returns multiple for each stock
    print(f'Ticker: {ticker}; Returns Multiple against S&P 500: {returns_multiple}\n')

    # Pause for 1 second to avoid overloading the server with requests
    time.sleep(1)

# Create dataframe with returns multiples and corresponding Relative Strength (RS) rating
rs_df = pd.DataFrame(list(zip(sp500_tickers, returns_multiples)), columns=['Ticker', 'Returns_Multiple'])
rs_df['RS_Rating'] = rs_df.Returns_Multiple.rank(pct=True) * 100

# Print RS ratings for all stocks
print(rs_df)