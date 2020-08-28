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

df['200MA'] = df['Adj Close'].rolling(200).mean()
df['SMA10'] = ta.SMA(df['Adj Close'], timeperiod=10)
df['SMA15'] = ta.SMA(df['Adj Close'], timeperiod=15)
df['SMA50'] = ta.SMA(df['Adj Close'], timeperiod=50)
df['SMA65'] = ta.SMA(df['Adj Close'], timeperiod=65)
df['SMA75'] = ta.SMA(df['Adj Close'], timeperiod=75)
df['SMA100'] = ta.SMA(df['Adj Close'], timeperiod=100)
df['SMA130'] = ta.SMA(df['Adj Close'], timeperiod=130)
df['SMA195'] = ta.SMA(df['Adj Close'], timeperiod=195)

df['ROC10'] = ta.ROC(df['SMA10'], timeperiod=10)
df['ROC15'] = ta.ROC(df['SMA10'], timeperiod=15)
df['ROC20'] = ta.ROC(df['SMA10'], timeperiod=20)
df['ROC30'] = ta.ROC(df['SMA15'], timeperiod=30)
df['ROC40'] = ta.ROC(df['SMA50'] , timeperiod=40)
df['ROC65'] = ta.ROC(df['SMA65'], timeperiod=65)
df['ROC75'] = ta.ROC(df['SMA75'], timeperiod=75)
df['ROC100'] = ta.ROC(df['SMA100'], timeperiod=100)
df['ROC195'] = ta.ROC(df['SMA130'], timeperiod=100)
df['ROC265'] = ta.ROC(df['SMA130'], timeperiod=265)
df['ROC390'] = ta.ROC(df['SMA130'], timeperiod=390)
df['ROC530'] = ta.ROC(df['SMA195'], timeperiod=530)
df['Special_K'] = (df['ROC10'] * 1) + (df['ROC15'] * 2) + (df['ROC20'] * 3) + (df['ROC30']) * 4 + (df['ROC40'] * 1) + (df['ROC65'] * 2) + (df['ROC75'] * 3) + (df['ROC100'] * 4) + (df['ROC195'] * 1) + (df['ROC265'] * 2) + (df['ROC390'] * 3) + (df['ROC530'] * 4)
df['200MAk'] = df['Special_K'].rolling(5).mean()
df = df.dropna()

# Line Chart
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df.index, df['Adj Close'])
ax1.plot(df.index, df['200MA'])
ax1.axhline(y=df['Adj Close'].mean(),color='r')
ax1.grid()
#ax1.grid(True, which='both')
#ax1.grid(which='minor', linestyle='-', linewidth='0.5', color='black')
#ax1.grid(which='major', linestyle='-', linewidth='0.5', color='red')
#ax1.minorticks_on()
#ax1.legend(loc='best')
ax1v = ax1.twinx()
ax1v.fill_between(df.index[0:],0, df.Volume[0:], facecolor='#0079a3', alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Special_K'], label='Special K')
ax2.plot(df['200MA'])
ax2.grid()
ax2.set_ylabel('Special K')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()

# ## Candlestick with Martin Pring Special K
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
ax1.plot(df.index, df['200MA'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
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
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Special_K'], label='Special K')
ax2.plot(df['200MA'])
ax1.axhline(y=0,color='r')
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()