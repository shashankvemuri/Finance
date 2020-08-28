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
start = dt.date.today() - dt.timedelta(days = 365*2)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

import talib as ta

e1 = ta.EMA(df['Adj Close'], timeperiod=3)
e2 = ta.EMA(e1, timeperiod=3)
e3 = ta.EMA(e2, timeperiod=3)
e4 = ta.EMA(e3, timeperiod=3)
e5 = ta.EMA(e4, timeperiod=3)
e6 = ta.EMA(e5, timeperiod=3)
# a is the volume factor, default value is 0.7 but 0.618 can also be used
a = 0.7
c1 = -a**3
c2 = (3*a**2) + (3*a**3)
c3 = - (6*a**2) - (3*a) - (3*a**3)
c4 = 1 + (3*a) + (a**3) + (3*a**2)

df['T3'] = c1*e6 + c2*e5 + c3*e4 + c4*e3
df = df.dropna()

from matplotlib import dates as mdates
df['VolumePositive'] = df['Open'] < df['Adj Close']
df = df.dropna()
df = df.reset_index()
df['Date'] = mdates.date2num(df['Date'].tolist())

from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(20,16))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['T3'],label='T3')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')
plt.show()


fig = plt.figure(figsize=(20,16))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['T3'],label='T3')
ax1.step(df.Date, df['Low'], c='blue', linestyle='--', label='Low')
ax1.step(df.Date, df['High'], c='red', linestyle='--', label='High')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')
plt.show()

fig = plt.figure(figsize=(14,7))
ax1 = fig.add_subplot(111)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
plt.plot(df.Date, df['T3'],marker='o',label='T3')
for i,j in zip(df.Date, round(df['T3'],2)):
    ax1.annotate(j, xy=(i, j))
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')
plt.show()

fig = plt.figure(figsize=(14,7))
ax1 = fig.add_subplot(111)
candlestick_ohlc(ax1,df.values[80:], width=0.5, colorup='g', colordown='r', alpha=1.0)
plt.plot(df.iloc[80:, 0], df['T3'][80:],marker='o',label='T3')
for i,j in zip(df.Date[100:], round(df['T3'],2)):
    ax1.annotate(j, xy=(i, j))
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.iloc[80:, 0], df['Volume'][80:], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')
plt.show()