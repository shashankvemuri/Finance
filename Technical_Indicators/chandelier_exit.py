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

import talib as ta
df['ATR'] = ta.ATR(df['High'], df['Low'], df['Adj Close'], timeperiod=22)
df['High_22'] = df['High'].rolling(22).max()
df['Low_22'] = df['Low'].rolling(22).min()

df['CH_Long'] = df['High_22'] - df['ATR'] * 3 
df['CH_Short'] = df['Low_22'] + df['ATR'] * 3

df = df.dropna()

plt.figure(figsize=(16,10))
plt.plot(df['Adj Close'])
plt.plot(df['CH_Long'])
plt.title('Chandelier Exit for Long')
plt.legend(loc='best')
plt.ylabel('Price')
plt.xlabel('Date')
plt.show()

plt.figure(figsize=(16,10))
plt.plot(df['Adj Close'])
plt.plot(df['CH_Short'])
plt.title('Chandelier Exit for Short')
plt.legend(loc='best')
plt.ylabel('Price')
plt.xlabel('Date')
plt.show()

plt.figure(figsize=(16,10))
plt.plot(df['Adj Close'])
plt.plot(df['CH_Long'])
plt.plot(df['CH_Short'])
plt.title('Chandelier Exit for Long & Short')
plt.legend(loc='best')
plt.ylabel('Price')
plt.xlabel('Date')
plt.show()


# ## Candlestick with Chandelier Exit
from matplotlib import dates as mdates
df['VolumePositive'] = df['Open'] < df['Adj Close']
df = df.dropna()
df = df.reset_index()
df['Date'] = mdates.date2num(df['Date'].tolist())

from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['CH_Long'])
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Chandelier Exit for Long')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
ax1.legend(loc='best')
plt.show()

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['CH_Short'], color='Orange')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Chandelier Exit for Short')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
ax1.legend(loc='best')
plt.show()

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['CH_Long'])
ax1.plot(df.Date, df['CH_Short'])
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Chandelier Exit for Long & Short')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
ax1.legend(loc='best')
plt.show()