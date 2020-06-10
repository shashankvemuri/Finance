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

short_term=5
long_term=20
vwma_lt = ((df['Adj Close']*df['Volume'])+(df['Adj Close'].shift(1)*df['Volume'].shift(1))+(df['Adj Close'].shift(2)*df['Volume'].shift(2))) / (df['Volume'].rolling(long_term).sum())

vwma_st = ((df['Adj Close']*df['Volume'])+(df['Adj Close'].shift(1)*df['Volume'].shift(1))+(df['Adj Close'].shift(2)*df['Volume'].shift(2))) / (df['Volume'].rolling(short_term).sum())

vpc = vwma_lt - df['Adj Close'].rolling(long_term).mean()
vpr = vwma_st / df['Adj Close'].rolling(short_term).mean()
vm = df['Adj Close'].rolling(short_term).mean()/ df['Adj Close'].rolling(long_term).mean()
vpci = vpc * vpr * vm
df['VPCI'] = vpci

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.grid(True, which='both')
#ax1.grid(which='minor', linestyle='-', linewidth='0.5', color='black')
#ax1.grid(which='major', linestyle='-', linewidth='0.5', color='red')
#ax1.minorticks_on()
ax1.legend(loc='best')
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['VPCI'], '-', label='Volume Price Confirmation Indicator')
#ax2.axhline(y=0,color='r')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()

# ## Candlestick with VPCI
from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = pd.to_datetime(dfc['Date'])
dfc['Date'] = dfc['Date'].apply(mdates.date2num)

from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(3, 1, 1)
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

ax2 = plt.subplot(3, 1, 2)
df['VolumePositive'] = df['Open'] < df['Adj Close']
ax2.bar(df.index, df['Volume'], color=df.VolumePositive.map({True: 'g', False: 'r'}), label='macdhist')
ax2.grid()
ax2.set_ylabel('Volume')

ax3 = plt.subplot(3, 1, 3)
ax3.plot(df['VPCI'])
ax3.grid()
ax3.set_ylabel('Volume Price Confirmation Indicator')
ax3.set_xlabel('Date')
ax3.legend()
plt.show()