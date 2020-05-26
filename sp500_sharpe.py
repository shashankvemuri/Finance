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
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
import seaborn as sns


start_date = datetime.datetime(2019,1,15)
end_date = datetime.date.today()


tickers = si.tickers_sp500()
tickers = [item.replace(".", "-") for item in tickers]

sharpe_ratios = []

for ticker in tickers:
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

np.savez("sharpe_ratios(1).npz", sharpe_ratios)

all_sharpe_ratios = np.load("sharpe_ratios(1).npz")
all_sharpe_ratios = all_sharpe_ratios['arr_0'] 
all_sharpe_ratios = all_sharpe_ratios.tolist()

# Create a dataframe with each company and their corressponding beta/alpha values
dataframe = pd.DataFrame(list(zip(tickers, all_sharpe_ratios)), columns =['Company', 'Sharpe_Ratio']) 

# Sorting the dataframe from highest sharpe values to lowest
sort_by_sharpe = dataframe.sort_values('Sharpe_Ratio', ascending = True)
sort_by_sharpe = sort_by_sharpe.dropna()

sort_by_sharpe.to_csv(r'/Users/shashank/Downloads/csv/sp_ratios.csv')

sort_by_sharpe = pd.read_csv('/Users/shashank/Downloads/csv/sp_ratios.csv')
sort_by_sharpe = sort_by_sharpe.drop(['Unnamed: 0'], axis = 1)
df = sort_by_sharpe

print (df.tail())