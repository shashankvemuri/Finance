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
start = dt.date.today() - dt.timedelta(days = 365)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

from zigzag import *
plt.figure(figsize=(14,7))

pivots = peak_valley_pivots(df['Adj Close'].values, 0.2, -0.2)
ts_pivots = pd.Series(df['Adj Close'], index=df.index)
ts_pivots = ts_pivots[pivots != 0]
df['Adj Close'].plot()
ts_pivots.plot(style='g-o', label='ZigZag')
plt.title('Stock of ZigZag', fontsize=18)
plt.legend(loc='best')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# ## Candlestick with ZigZag
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
pivots = peak_valley_pivots(df['Adj Close'].values, 0.2, -0.2)
ts_pivots = pd.Series(df['Adj Close'], index=df.index)
ts_pivots = ts_pivots[pivots != 0]
ax1.plot(df['Adj Close'])
ts_pivots.plot(style='g-o', label='ZigZag')
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
ax1.set_xlabel('Date')
ax1.legend()
plt.show()