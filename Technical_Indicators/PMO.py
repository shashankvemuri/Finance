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
df['35_Custom_EMA_ROC'] = df['ROC'].ewm(ignore_na=False,span=35,min_periods=0,adjust=True).mean()
df['35_Custom_EMA_ROC_10'] = df['35_Custom_EMA_ROC']*10
df['PMO_Line'] = df['35_Custom_EMA_ROC_10'].ewm(ignore_na=False,span=20,min_periods=0,adjust=True).mean()
df['PMO_Signal_Line'] = df['PMO_Line'].ewm(ignore_na=False,span=10,min_periods=0,adjust=True).mean()
df = df.dropna()

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['PMO_Line'], label='PMO Line')
ax2.plot(df['PMO_Signal_Line'], label='PMO Signal Line')
ax2.axhline(y=0, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('PMO')
ax2.set_xlabel('Date')
plt.show()

# ## Candlestick with PMO
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

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['PMO_Line'], label='PMO_Line')
ax2.plot(df['PMO_Signal_Line'], label='PMO_Signal_Line')
ax2.axhline(y=0, color='red')
ax2.grid()
ax2.set_ylabel('PMO')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()