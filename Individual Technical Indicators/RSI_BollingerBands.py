import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'NIO'
start = dt.date.today() - dt.timedelta(days = 365*2)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

# Simple Line Chart
plt.figure(figsize=(14,10))
plt.plot(df['Adj Close'])
plt.legend(loc='best')
plt.title('Stock '+ symbol +' Closing Price')
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
plt.title(f'30 Day Bollinger Band for {symbol}')
plt.ylabel('Price')
plt.legend(loc='best')
plt.show()

dfc = df.copy()
dfc = dfc.reset_index()

from matplotlib import dates as mdates
dfc['Date'] = mdates.date2num(dfc['Date'].astype(dt.date))

# This one has not date and is convert to number
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax = plt.subplot(1,1,1)
candlestick_ohlc(ax,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
plt.title('Candlestick Chart of Stock')
plt.ylabel('Price')
plt.show()

# Plot Candlestick with dates
fig = plt.figure(figsize=(14,7))
ax = plt.subplot(1,1,1)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
candlestick_ohlc(ax,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
plt.title('Candlestick Chart of Stock')
plt.ylabel('Price')
plt.show()

# ## Combine RSI and Bollinger Bands
fig = plt.figure(figsize=(14,7))
ax = plt.subplot(2,1,2)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
plt.plot(df[['20 Day MA', 'Upper Band', 'Lower Band']], label=('20 Day MA', 'Upper Band', 'Lower Band'))
candlestick_ohlc(ax,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
plt.title('RSI & Bollinger Bands')
plt.ylabel('Price')

plt.plot(rsi, '-', label='RSI')
plt.text(s='Overbought', x=rsi.index[0], y=80, fontsize=14)
plt.text(s='OverSold', x=rsi.index[0], y=20, fontsize=14)
ax.axhline(y=80,color='r')
ax.axhline(y=20,color='r')
plt.xlabel('Date')
plt.legend(loc='best')
plt.show()