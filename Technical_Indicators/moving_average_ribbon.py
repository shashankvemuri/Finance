import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days = 180)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)


df['MA10'] = df['Adj Close'].rolling(10).mean()
df['MA20'] = df['Adj Close'].rolling(20).mean()
df['MA30'] = df['Adj Close'].rolling(30).mean()
df['MA40'] = df['Adj Close'].rolling(40).mean()
df['MA50'] = df['Adj Close'].rolling(50).mean()
df['MA60'] = df['Adj Close'].rolling(60).mean()

import talib as ta

df['SMA5'] = ta.SMA(df['Adj Close'], timeperiod=5)
df['SMA15'] = ta.SMA(df['Adj Close'], timeperiod=15)
df['SMA25'] = ta.SMA(df['Adj Close'], timeperiod=25)
df['SMA35'] = ta.SMA(df['Adj Close'], timeperiod=35)
df['SMA45'] = ta.SMA(df['Adj Close'], timeperiod=45)

df['EMA5'] = ta.EMA(df['Adj Close'], timeperiod=5)
df['EMA15'] = ta.EMA(df['Adj Close'], timeperiod=15)
df['EMA25'] = ta.EMA(df['Adj Close'], timeperiod=25)
df['EMA35'] = ta.EMA(df['Adj Close'], timeperiod=35)
df['EMA45'] = ta.EMA(df['Adj Close'], timeperiod=45)

# Line Chart
df[['Adj Close', 'MA10', 'MA20', 'MA30', 'MA40', 'MA50', 'MA60']].plot(figsize=(16,8))
plt.title('Stock '+ symbol +' Closing Price of MA')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='Best')
plt.show()

df[['Adj Close', 'SMA5', 'SMA15', 'SMA25', 'SMA35', 'SMA45']].plot(figsize=(16,8))
plt.title('Stock '+ symbol +' Closing Price of SMA')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='Best')
plt.show()

df[['Adj Close', 'EMA5', 'EMA15', 'EMA25', 'EMA35', 'EMA45']].plot(figsize=(16,8))
plt.title('Stock '+ symbol +' Closing Price of EMA')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

from matplotlib import dates as mdates

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(16,8))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(dfc.Date, dfc[['EMA5', 'EMA15', 'EMA25', 'EMA35', 'EMA45']])
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
ax1v.fill_between(dfc.Date, 0, dfc.Volume[0:], facecolor='#0079a3', alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
plt.show()