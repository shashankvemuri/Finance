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

n = 7
UBB = df['High'] * ( 1 + 4 * (df['High'] - df['Low']) / (df['High'] + df['Low']))
df['Upper_Band'] = UBB.rolling(n, center=False).mean()
df['Middle_Band'] = df['Adj Close'].rolling(n).mean()
LBB = df['Low'] * ( 1 - 4 * (df['High'] - df['Low']) / (df['High'] + df['Low']))
df['Lower_Band'] = LBB.rolling(n, center=False).mean()

plt.figure(figsize=(15,7))
plt.plot(df['Adj Close'])
plt.plot(df['Upper_Band'])
plt.plot(df['Middle_Band'])
plt.plot(df['Lower_Band'])
plt.ylabel('Price')
plt.xlabel('Date')
plt.title('Stock Closing Price of ' + str(n) + '-Day Acceleration Bands')
plt.legend(loc='best')
plt.show()

from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = pd.to_datetime(dfc['Date'])
dfc['Date'] = dfc['Date'].apply(mdates.date2num)
from mplfinance.original_flavor import candlestick_ohlc

fig = plt.figure(figsize=(15,7))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df['Upper_Band'], label='Upper Band')
ax1.plot(df['Middle_Band'], label='Middle Band')
ax1.plot(df['Lower_Band'], label='Lower Band')
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
ax1.legend(loc='best')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
plt.show()