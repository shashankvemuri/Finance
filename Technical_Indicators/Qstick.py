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
#EMAC = ta.EMA(df['Adj Close'], timeperiod=10)
#EMAO = ta.EMA(df['Open'], timeperiod=10)
CO = df['Adj Close'] - df['Open']
#df['QStick'] = EMAC - EMAO
df['QStick'] = ta.EMA(CO, timeperiod=10)

# Line Chart
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df.index, df['Adj Close'])
ax1.axhline(y=df['Adj Close'].mean(),color='r')
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df.index, df['QStick'], label='Qstick')
ax2.axhline(y=df['QStick'].mean(),color='r')
ax2.grid()
ax2.set_ylabel('QStick')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()

# ## Candlestick with QStick
from matplotlib import dates as mdates
dfc = df.copy()
dfc['QStick'] = (dfc['Adj Close'] - dfc['Open']).rolling(10).mean() 
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(16,12))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(dfc.index, dfc['QStick'], label='QStick')
ax2.axhline(y=0,color='r', linestyle='--')
ax2.grid()
ax2.set_ylabel('QStick')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()

fig = plt.figure(figsize=(16,12))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
dfc['Positive'] = dfc['QStick'] > 0
ax2.bar(dfc.index, dfc['QStick'], color=dfc.Positive.map({True: 'g', False: 'r'}), label='QStick')
ax2.axhline(y=0,color='r', linestyle='--')
ax2.grid()
ax2.set_ylabel('QStick')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()