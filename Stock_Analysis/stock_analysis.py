import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import datetime as dt
import talib as ta

stock = 'AAPL'
n = 30 # number of periods
window = 252

num_of_years = 1
start = dt.date.today() - dt.timedelta(days=365*num_of_years)
end = dt.date.today()

df = pdr.get_data_yahoo(stock, start, end)

df['Daily_Returns'] = df['Adj Close'].shift(1) / df['Adj Close']  - 1
DR = df['Adj Close'].pct_change(1) # 1 is for "One Day" in the past
df['Log_Returns'] = np.log(df['Adj Close']) - np.log(df['Adj Close'].shift(1))


df['RSI']=ta.RSI(np.array(df['Adj Close'].shift(1)), timeperiod=n)
df['MA']=ta.MA(np.array(df['Adj Close'].shift(1)), timeperiod=n, matype=0)
df['SMA']=ta.SMA(np.array(df['Adj Close'].shift(1)))
df['EMA']=ta.EMA(np.array(df['Adj Close'].shift(1)), timeperiod=n)
df['VWAP'] = round(np.cumsum(df['Volume']*(df['High']+df['Low'])/2) / np.cumsum(df['Volume']), 2)

Maximum_Drawdown = df['Adj Close'].rolling(window, min_periods=1).max()
Daily_Drawdown = df['Adj Close']/Maximum_Drawdown - 1.0
Negative_Drawdown = Daily_Drawdown.rolling(window, min_periods=1).min()

plt.figure(figsize=(16,10))
df['Adj Close'].plot(grid=True)
plt.title("Stock Adj Close Price", fontsize=18, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Price",fontsize=12)
plt.show()

df[['High', 'Low', 'Adj Close']].plot(figsize=(16,10), grid=True)
plt.title("Stock Adj Close Price", fontsize=18, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Price", fontsize=12)
plt.show()


df['Daily_Returns'].plot(figsize=(12,6))
plt.title("Daily Returns",fontsize=18, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Price", fontsize=12)
plt.show()


df['Log_Returns'].plot(figsize=(12,6))
plt.title("Log Returns", fontsize=18, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Price", fontsize=12)
plt.show()


plt.figure(figsize=(16,10))
plt.hist(df['Daily_Returns'].dropna(), bins=100, label='Daily Returns data') # Drop NaN
plt.title("Histogram of Daily Returns", fontsize=18, fontweight='bold')
plt.axvline(df['Daily_Returns'].mean(), color='r', linestyle='dashed', linewidth=2) # Shows the average line
plt.xlabel("Probability", fontsize=12)
plt.ylabel("Daily Returns", fontsize=12)
plt.show()


plt.figure(figsize=(16,10))
Daily_Drawdown.plot()
Negative_Drawdown.plot(color='r',grid=True) 
plt.title("Maximum Drawdown", fontsize=18, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Price", fontsize=12)
plt.show()

DIV = pdr.get_data_yahoo(stock, start, end, actions='only')
print (DIV)

Total_Dividend = DIV['Dividends'].sum()
print (Total_Dividend)

HPR = (df['Adj Close'][502] + Total_Dividend - df['Adj Close'][0]) / df['Adj Close'][0]
print('Holding Period Return: ', str(round(HPR,4)*100)+"%")