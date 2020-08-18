from pandas_datareader import DataReader
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
    except (KeyError, RemoteDataError, TypeError, gaierror) as e:
        print (e)
        print ('-'*80)