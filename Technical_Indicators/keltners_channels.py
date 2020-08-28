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

n = 20
df['EMA'] = ta.EMA(df['Adj Close'], timeperiod=20)
df['ATR'] = ta.ATR(df['High'], df['Low'], df['Adj Close'], timeperiod=10)
df['Upper Line'] = df['EMA'] + 2*df['ATR']
df['Lower Line'] = df['EMA'] - 2*df['ATR']
del df['ATR']

plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
plt.plot(df['EMA'], label='Middle Line', linestyle='--')
plt.plot(df['Upper Line'], color='g')
plt.plot(df['Lower Line'], color='r')
plt.ylabel('Price')
plt.xlabel('Date')
plt.title(symbol + ' Closing Price of Keltners Channels')
plt.legend(loc='best')
plt.show()

# ## Candlestick with Keltners Channels
from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df['EMA'], label='Middle Line', linestyle='--')
ax1.plot(df['Upper Line'], color='g')
ax1.plot(df['Lower Line'], color='r')
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