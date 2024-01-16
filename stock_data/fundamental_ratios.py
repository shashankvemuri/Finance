import FundamentalAnalysis as fa
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from config import financial_model_prep

# Set the Yahoo Finance API override
yf.pdr_override()

# Get API key from config
api_key = financial_model_prep()

# Define a list of stock tickers
ticker_list = ['TMUSR', 'AAPL', 'MSFT', 'AMZN', 'FB', 'GOOGL', 'GOOG', 'INTC', 'NVDA', 'ADBE',
               'PYPL', 'CSCO', 'NFLX', 'PEP', 'TSLA']

# Download and save financial data for each stock
for ticker in ticker_list:
    # Get key metrics and financial ratios
    key_metrics = fa.key_metrics(ticker, api_key, period="annual")
    financial_ratios = fa.financial_ratios(ticker, api_key, period="annual")

    # Save data to Excel files
    key_metrics.to_excel(f'{ticker}_key_metrics.xlsx')
    financial_ratios.to_excel(f'{ticker}_financial_ratios.xlsx')

# Download stock price data for a specified date range
start_date = "2017-01-01"
stock_prices = pdr.get_data_yahoo(ticker_list, start=start_date)['Close']

# Save stock prices data to an Excel file
stock_prices.to_excel('stock_prices.xlsx')

# Print the latest data for each category
print('Key Metrics for last ticker: ')
print(key_metrics)

print('Financial Ratios for last ticker: ')
print(financial_ratios)

print('Price History for tickers since', start_date, ':')
print(stock_prices)