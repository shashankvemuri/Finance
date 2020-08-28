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
df['Upper_Channel_Line'] = df['High'].rolling(20).max()
df['Lower_Channel_Line'] = df['Low'].rolling(20).min()
df['Centerline'] = (df['Upper_Channel_Line'] + df['Lower_Channel_Line']) / 2
df = df.dropna()

df[['Adj Close','Upper_Channel_Line','Lower_Channel_Line','Centerline']].plot(figsize=(16,10))
plt.title('Price Channels for Stock')
plt.legend(loc='best')
plt.xlabel('Price')
plt.ylabel('Date')
plt.show()

ax = df[['Adj Close','Upper_Channel_Line','Lower_Channel_Line','Centerline']].plot(figsize=(16,10))
xtick = pd.date_range( start=df.index.min(), end=df.index.max(), freq='W')
ax.set_xticks(xtick, minor=True )
ax.grid('on', which='minor', axis='x')
ax.grid('off', which='major', axis='x')
plt.show()

import matplotlib.dates as mdates
months = mdates.MonthLocator()  # every month
fig, ax = plt.subplots(figsize=(16,8))
datemin = np.datetime64(df.index[0], 'M')
datemax = np.datetime64(df.index[-1], 'M') + np.timedelta64(1, 'M')
ax.set_xlim(datemin, datemax)

ax.plot(df.index, df['Adj Close'], color='blue')
ax.plot(df.index, df['Upper_Channel_Line'], color='red')
ax.plot(df.index, df['Lower_Channel_Line'], color='red')
ax.plot(df.index, df['Centerline'], color='red', linestyle='--')
ax.xaxis.set_minor_locator(months)
ax.grid(True)

ax.set_title('Price Channels for Stock')
ax.set_ylabel('Price')
ax.set_xlabel('Date')
ax.legend(loc='best')

plt.figure(figsize=(16,10))
plt.plot(df['Adj Close'])
plt.plot(df['Upper_Channel_Line'], color='r')
plt.plot(df['Lower_Channel_Line'], color='r')
plt.plot(df['Centerline'], color='r', linestyle='--')
plt.title('Price Channels for Stock')
plt.legend(loc='best')
plt.ylabel('Price')
plt.xlabel('Date')
plt.show()

# ## Candlestick with Price Channels
from matplotlib import dates as mdates
df['VolumePositive'] = df['Open'] < df['Adj Close']
df = df.dropna()
df = df.reset_index()
df['Date'] = mdates.date2num(df['Date'].tolist())

from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.dates import MonthLocator, YearLocator
fig, ax1 = plt.subplots(figsize=(16,8))
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['Upper_Channel_Line'], color='red')
ax1.plot(df.Date, df['Lower_Channel_Line'], color='red')
ax1.plot(df.Date, df['Centerline'], color='red', linestyle='--')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
#ax1.axhline(y=dfc['Adj Close'].mean(),color='r')

#yloc = YearLocator()
#ax1.xaxis.set_major_locator(yloc)
mloc = MonthLocator()
ax1.xaxis.set_minor_locator(mloc)
ax1.grid(True)
#ax1.grid(True, which='major', linestyle='-', linewidth='0.5', color='black')
#ax1.grid(True, which='minor', linestyle=':', linewidth='0.5', color='black')

ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Price Channels for Stock')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
ax1.legend(loc='best')
plt.show()

from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.dates import MonthLocator, YearLocator
fig, ax1 = plt.subplots(figsize=(16,8))
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df.Date, df['Upper_Channel_Line'], color='red')
ax1.plot(df.Date, df['Lower_Channel_Line'], color='red')
ax1.plot(df.Date, df['Centerline'], color='red', linestyle='--')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
xtick = pd.date_range(start=df.Date.min(), end=df.Date.max(), freq='W')
ax1.grid(True)
ax1.set_xticks(xtick, minor=True)
ax1.grid('on', which='minor', axis='x')
ax1.grid('off', which='major', axis='x')

ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Price Channels for Stock')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
ax1.legend(loc='best')
plt.show()