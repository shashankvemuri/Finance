import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from pylab import rcParams

# input
symbol = 'NIO'
start = dt.date.today() - dt.timedelta(days = 365*2)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

# Simple Line Chart
plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
plt.legend(loc='best')
plt.title(symbol +' Closing Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# ## RSI
import talib as ta
rsi = ta.RSI(df['Adj Close'], timeperiod=14)
rsi = rsi.dropna()

# ## Bollinger Bands
# Create Bollinger Band
# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:bollinger_bands
df['20 Day MA'] = df['Adj Close'].rolling(window=20).mean()
df['20 Day STD'] = df['Adj Close'].rolling(window=20).std()
df['Upper Band'] = df['20 Day MA'] + (df['20 Day STD'] * 2)
df['Lower Band'] = df['20 Day MA'] - (df['20 Day STD'] * 2)

df[['Adj Close', '20 Day MA', 'Upper Band', 'Lower Band']].plot(figsize=(14,7))
plt.title(f'30 Day Bollinger Band for {symbol.upper()}')
plt.ylabel('Price')
plt.legend(loc='best')
plt.show()

dfc = df.copy()
dfc = dfc.reset_index()

from matplotlib import dates as mdates
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())

# This one has not date and is convert to number
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax = plt.subplot(1,1,1)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
candlestick_ohlc(ax,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
plt.title(f'{symbol.upper()} Candlestick Chart')
plt.ylabel('Price')
plt.show()

# ## Combine RSI and Bollinger Bands
rcParams['figure.figsize'] = 14, 7
ax = plt.subplot(211)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
plt.plot(df[['20 Day MA', 'Upper Band', 'Lower Band']], label=('20 Day MA', 'Upper Band', 'Lower Band'))
candlestick_ohlc(ax,dfc.values, width=.5, colorup='g', colordown='r', alpha=1.0)
plt.title(f'Bollinger Bands & RSI for {symbol.upper()}')
plt.ylabel('Price')

plt.subplot(212)
plt.plot(rsi, '-', label='RSI')
plt.text(s='Overbought', x=rsi.index[0], y=70, fontsize=8)
plt.text(s='OverSold', x=rsi.index[0], y=30, fontsize=8)
plt.axhline(y=70,color='r')
plt.axhline(y=30,color='r')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.legend(loc='best')
plt.show()