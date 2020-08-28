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

df['ROC'] = ((df['Adj Close'] - df['Adj Close'].shift(1))/df['Adj Close'].shift(1)) * 100
df['ROC_Volume'] = ((df['Volume'] - df['Volume'].shift(1))/df['Volume'].shift(1)) * 100
df['NVI_Value'] = 0
df['NVI_Cumulative'] = 0
df1 = df[df['ROC_Volume']<0]
df1['NVI_Value'] = df1['ROC']
df[df['ROC_Volume']<0] = df1
df['NVI_Cumulative'] = 1000+df['NVI_Value'].cumsum()

# Drop Columns
df = df.drop(['ROC','ROC_Volume'],axis=1)

import talib as ta
df['EMA_100'] = ta.EMA(df['Adj Close'], timeperiod=100)
df['EMA_255'] = ta.EMA(df['Adj Close'], timeperiod=255)
df['NVI_100'] = ta.EMA(df['NVI_Cumulative'], timeperiod=100)
df['NVI_255'] = ta.EMA(df['NVI_Cumulative'], timeperiod=255)

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.plot(df['EMA_100'])
ax1.plot(df['EMA_255'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['NVI_Cumulative'], label='NVI')
ax2.plot(df['NVI_100'])
ax2.plot(df['NVI_255'])
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('NVI')
ax2.set_xlabel('Date')
plt.show()

# ## Candlestick with NVI
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
ax1.plot(df['EMA_100'])
ax1.plot(df['EMA_255'])
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
ax2.legend(loc='best')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['NVI_Cumulative'], label='NVI')
ax2.plot(df['NVI_100'])
ax2.plot(df['NVI_255'])
ax2.grid()
ax2.set_ylabel('NVI')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()