import FundamentalAnalysis as fa
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from config import financial_model_prep

# Set the Yahoo Finance API key
yf.pdr_override()
api_key = financial_model_prep()

# Define a list of stocks to fetch financial data for
ticker_list = ['TMUSR', 'AAPL', 'MSFT', 'AMZN', 'FB', 'GOOGL', 'GOOG', 'INTC', 'NVDA', 'ADBE',
               'PYPL', 'CSCO', 'NFLX', 'PEP', 'TSLA']

# Download financial indicators data and output as Excel files for each stock
for ticker in ticker_list:
    # Get key metrics
    key_metrics_annually = fa.key_metrics(ticker, api_key, period="annual")
    # Save key metrics data to an Excel file
    with pd.ExcelWriter(f'{ticker}_key_metrics.xlsx') as writer:
        key_metrics_annually.to_excel(writer, ticker)

    # Get financial ratios
    financial_ratios_annually = fa.financial_ratios(ticker, api_key, period="annual")
    # Save financial ratios data to an Excel file
    with pd.ExcelWriter(f'{ticker}_financial_ratios.xlsx') as writer:
        financial_ratios_annually.to_excel(writer, ticker)

# Download stock prices for the specified date range
data = pdr.get_data_yahoo(ticker_list, start="2017-01-01")
price = data.loc[:, 'Close']
# Save stock prices data to an Excel file
price.to_excel(f'{ticker}_price.xlsx')

# Print key metrics
print ('Key Metrics: ')
print (key_metrics_annually)

# Print financial ratios
print ('Financial Ratios: ')
print (financial_ratios_annually)

# Print price history
print ('Price History: ')
print (price)