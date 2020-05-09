# .npz    - past 5 years
# (1).npz - past year
# (2).npz - past 6 months
# (3).npz - past 3 months
# (4).npz - past month

# ROLLING SHARPE RATIO
import pickle
import datetime
import requests
import bs4 as bs
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
from pandas_datareader._utils import RemoteDataError
import seaborn as sns
from yahoo_fin import stock_info as si

pd.set_option('display.max_rows', None)
pd.set_option('display.min_rows', None)

start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

nasdaq_tickers = si.tickers_nasdaq()
sharpe_ratios = []
invalid_tickers = []

for ticker in nasdaq_tickers:
    try:
        df = DataReader(ticker, 'yahoo', start_date, end_date) 
        x = 5000
        
        y = (x)
        
        stock_df = df
        stock_df['Norm return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']
        
        allocation = float(x/y)
        stock_df['Allocation'] = stock_df['Norm return'] * allocation
        
        stock_df['Position'] = stock_df['Allocation'] * x
        pos = [df['Position']]
        val = pd.concat(pos, axis=1)
        val.columns = ['WMT Pos']
        val['Total Pos'] = val.sum(axis=1)
        
        val.tail(1)
        
        val['Daily Return'] = val['Total Pos'].pct_change(1)
        
        Sharpe_Ratio = val['Daily Return'].mean() / val['Daily Return'].std()
        
        A_Sharpe_Ratio = (252**0.5) * Sharpe_Ratio
        
        print('---------------------------------------------------------------')
        print ('{} has an average annualized sharpe ratio of {}'.format(ticker, A_Sharpe_Ratio))
        
        sharpe_ratios.append(A_Sharpe_Ratio)
    except (KeyError, RemoteDataError, ZeroDivisionError):
        invalid_tickers.append(ticker)

'''
np.savez('invalid_nasdaq_tickers.npz', invalid_tickers)
np.savez("nasdaq_sharpe_ratios(1).npz", sharpe_ratios)
'''
'''
all_sharpe_ratios = np.load("nasdaq_sharpe_ratios(1).npz")
all_sharpe_ratios = all_sharpe_ratios['arr_0'] 
all_sharpe_ratios = all_sharpe_ratios.tolist()

all_invalid_tickers = np.load("invalid_nasdaq_tickers.npz")
all_invalid_tickers = all_invalid_tickers['arr_0'] 
all_invalid_tickers = all_invalid_tickers.tolist()

set1 = set(nasdaq_tickers)
set2 = set(all_invalid_tickers)
set_difference = set1.difference(set2)
subtracted_list = list(set_difference)

tickers = subtracted_list

# Create a dataframe with each company and their corressponding beta/alpha values
nasdaq = pd.DataFrame(list(zip(tickers, all_sharpe_ratios)), columns =['Company', 'Sharpe_Ratio']) 

# Sorting the dataframe from highest sharpe values to lowest
sort_by_sharpe = nasdaq.sort_values('Sharpe_Ratio', ascending = True)
sort_by_sharpe = sort_by_sharpe.dropna()

print (len(all_invalid_tickers))
print (len(sort_by_sharpe))
print (len(tickers))

sort_by_sharpe.to_csv(r'nasdaq_ratios.csv')
'''
sort_by_sharpe = pd.read_csv('/Users/shashank/Downloads/csv/nasdaq_ratios.csv')
sort_by_sharpe = sort_by_sharpe.drop(['Unnamed: 0'], axis = 1)
nasdaq_df = sort_by_sharpe

print (nasdaq_df.tail())