import csv
import pandas_datareader as pdr
from pandas_datareader import DataReader
from pandas_datareader import data, wb
from datetime import date
import numpy as np
import pandas as pd
import datetime
from socket import gaierror
from pandas_datareader._utils import RemoteDataError
from yahoo_fin import stock_info as si


risk_free_return = 0.02

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

nasdaq_tickers = si.tickers_nasdaq()
index_ticker = '^GSPC'
start = datetime.datetime.now() - datetime.timedelta(days=365)
end = datetime.date.today()

expected_returns = []
invalid_tickers = []

for ticker in nasdaq_tickers:
    try:
        
        stock = DataReader(ticker, 'yahoo', start, end)
    
        index = DataReader(index_ticker, 'yahoo', start, end)
        
        return_s1 = stock.resample('M').last()
        return_s2 = index.resample('M').last()
            
        dataframe = pd.DataFrame({'s_adjclose' : return_s1['Adj Close'], 'm_adjclose': return_s2['Adj Close']}, index=return_s1.index)
            
        dataframe[['s_returns','m_returns']] = np.log(dataframe[['s_adjclose', 'm_adjclose']]/dataframe[['s_adjclose', 'm_adjclose']].shift(1))
            
        dataframe = dataframe.dropna()
        
        covmat = np.cov(dataframe["s_returns"], dataframe["m_returns"])
            
        beta = covmat[0,1]/covmat[1,1]
        
        beta, alpha = np.polyfit(dataframe["m_returns"], dataframe["s_returns"], deg=1)
        
        expected_return = risk_free_return + beta*(dataframe["m_returns"].mean()*12-risk_free_return)
        print ('{}:'.format(ticker))
        print("Expected Return: ", expected_return)
        print ('-'*80)
        
        expected_returns.append(expected_return)
    
    except (KeyError, RemoteDataError, TypeError, gaierror):
        invalid_tickers.append(ticker)

np.savez('invalid_nasdaq_tickers.npz', invalid_tickers)
np.savez("expected_nasdaq_returns.npz", expected_returns)

'''
invalid_tickers = np.load("/Users/shashank/Downloads/invalid_nasdaq_tickers.npz")
invalid_tickers = invalid_tickers['arr_0'] 
invalid_tickers = invalid_tickers.tolist()
#print (len(invalid_tickers))


set1 = set(nasdaq_tickers)
set2 = set(invalid_tickers)
set_difference = set1.difference(set2)
subtracted_list = list(set_difference)

tickers = subtracted_list

expected_returns = np.load("expected_returns.npz")
expected_returns = expected_returns['arr_0'] 
expected_returns = expected_returns.tolist()
##print (expected_returns)

# Create a dataframe with each company and their corressponding expected returns
dataframe = pd.DataFrame(
    {'Company': tickers,
     'Expected_Returns': expected_returns
    })
##print (dataframe)


# Sorting the dataframe from highest expected returns to lowest
sort_by_expected_return = dataframe.sort_values('Expected Returns', ascending = False)
print(sort_by_expected_return)
sort_by_expected_return.to_csv('Nasdaq_returns.csv')
'''