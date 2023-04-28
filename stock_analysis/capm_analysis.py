# Import necessary libraries
from pandas_datareader import DataReader
import numpy as np
import pandas as pd
import datetime
from socket import gaierror
from pandas_datareader._utils import RemoteDataError
from yahoo_fin import stock_info as si

# Define risk-free return rate
risk_free_return = 0.02

# Set pandas options for display
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Get all tickers in NASDAQ stock exchange
nasdaq_tickers = si.tickers_nasdaq()

# Define the ticker for index
index_ticker = '^GSPC'

# Define start and end date
start = datetime.datetime.now() - datetime.timedelta(days=365)
end = datetime.date.today()

# List to hold all expected returns
expected_returns = []

# Loop through each ticker in NASDAQ and calculate expected returns
for ticker in nasdaq_tickers:
    try:
        # Fetch stock and index data
        stock = DataReader(ticker, 'yahoo', start, end)
        index = DataReader(index_ticker, 'yahoo', start, end)
        
        # Resample to monthly data
        return_s1 = stock.resample('M').last()
        return_s2 = index.resample('M').last()
            
        # Create a dataframe to hold stock and index returns
        dataframe = pd.DataFrame({'s_adjclose': return_s1['Adj Close'], 'm_adjclose': return_s2['Adj Close']}, index=return_s1.index)
        dataframe[['s_returns', 'm_returns']] = np.log(dataframe[['s_adjclose', 'm_adjclose']] / dataframe[['s_adjclose', 'm_adjclose']].shift(1))
        dataframe = dataframe.dropna()
        
        # Calculate beta and alpha using linear regression
        covmat = np.cov(dataframe["s_returns"], dataframe["m_returns"])
        beta = covmat[0,1] / covmat[1,1]
        beta, alpha = np.polyfit(dataframe["m_returns"], dataframe["s_returns"], deg=1)
        
        # Calculate expected return using CAPM model
        expected_return = risk_free_return + beta * (dataframe["m_returns"].mean() * 12 - risk_free_return)
        
        # Print expected return for each ticker
        print('{}:'.format(ticker))
        print("Expected Return: ", expected_return)
        
        # Append expected return to list
        expected_returns.append(expected_return)
    
    except (KeyError, RemoteDataError, TypeError, gaierror) as e:
        # Handle exceptions
        print(e)