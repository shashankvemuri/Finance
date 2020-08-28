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

df['20SMA'] = ta.SMA(df['Adj Close'], timeperiod=20)
df['Upper_Envelope'] = df['20SMA'] + (df['20SMA'] * 0.025)
df['Lower_Envelope'] = df['20SMA'] - (df['20SMA'] * 0.025)

# Line Chart
plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
plt.plot(df['Upper_Envelope'], color='blue')
plt.plot(df['Lower_Envelope'], color='red')
plt.plot(df['Adj Close'].rolling(20).mean(), color='orange', label='Average Price', linestyle='--')
plt.title('Stock of Moving Average Envelopes')
plt.ylabel('Price')
plt.xlabel('Date')
plt.legend(loc='best')
plt.show()

# ## Candlestick with MAE
from matplotlib import dates as mdates

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df['Upper_Envelope'], color='blue')
ax1.plot(df['Lower_Envelope'], color='red')
ax1.plot(df['Adj Close'].rolling(20).mean(), color='orange')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.legend(loc='best')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
plt.show()