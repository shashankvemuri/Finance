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
start = dt.date.today() - dt.timedelta(days = 365*4)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

import talib as ta
upper, middle, lower = ta.BBANDS(df['Adj Close'])

# Create %B Indicator
df['BI'] = (df['Adj Close'] - lower)/(upper - lower)
df = df.dropna()

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.plot(upper, color='red')
ax1.plot(middle, color='red', linestyle='--')
ax1.plot(lower, color='red')
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['BI'], label='%B Indicator')
ax2.text(s='Overbought', x=df.index[30], y=1, fontsize=14, verticalalignment='top')
ax2.text(s='Oversold', x=df.index[30], y=0, fontsize=14, verticalalignment='bottom')
ax2.axhline(y=1, color='blue', linestyle='--')
ax2.axhline(y=0, color='green', linestyle='--')
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
plt.show()


# ## Candlestick with %B Indicator
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
ax1.plot(upper, color='red')
ax1.plot(middle, color='red', linestyle='--')
ax1.plot(lower, color='red')
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
ax2.plot(df['BI'], label='%B Indicator')
ax2.text(s='Overbought', x=df.index[30], y=1, fontsize=14, verticalalignment='top')
ax2.text(s='Oversold', x=df.index[30], y=0, fontsize=14, verticalalignment='bottom')
ax2.axhline(y=1, color='blue', linestyle='--')
ax2.axhline(y=0, color='green', linestyle='--')
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
plt.show()