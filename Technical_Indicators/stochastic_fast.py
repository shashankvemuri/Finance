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

n = 14 # number of days
s = 3 # smoothing
df['High_Highest'] = df['Adj Close'].rolling(n).max()
df['Low_Lowest'] = df['Adj Close'].rolling(n).min()
df['Fast_%K'] = ((df['Adj Close'] - df['Low_Lowest']) / (df['High_Highest'] - df['Low_Lowest'])) * 100
df['Fast_%D'] = df['Fast_%K'].rolling(s).mean()

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Fast_%K'], label='Fast %K')
ax2.plot(df['Fast_%D'], label='Fast %D')
ax2.text(s='Overbought', x=df.index[30], y=80, fontsize=14)
ax2.text(s='Oversold', x=df.index[30], y=20, fontsize=14)
ax2.axhline(y=80, color='red')
ax2.axhline(y=20, color='red')
ax2.grid()
ax2.set_ylabel('Fast Stochastic')
ax2.legend(loc='best')
ax2.set_xlabel('Date')
plt.show()

# ## Candlestick with Fast Stochastic
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
ax2.plot(df['Fast_%K'], label='Fast %K')
ax2.plot(df['Fast_%D'], label='Fast %D')
ax2.text(s='Overbought', x=df.index[30], y=80, fontsize=14)
ax2.text(s='Oversold', x=df.index[30], y=20, fontsize=14)
ax2.axhline(y=80, color='red')
ax2.axhline(y=20, color='red')
ax2.grid()
ax2.set_ylabel('Fast Stochastic')
ax2.legend(loc='best')
ax2.set_xlabel('Date')
plt.show()