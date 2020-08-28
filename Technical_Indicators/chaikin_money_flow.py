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

n = 20
df['MF_Multiplier'] = (2*df['Adj Close'] - df['Low'] - df['High'])/(df['High']-df['Low'])
df['MF_Volume'] = df['MF_Multiplier']*df['Volume']
df['CMF'] = df['MF_Volume'].rolling(n).sum()/df['Volume'].rolling(n).sum()
df = df.drop(['MF_Multiplier','MF_Volume'],axis=1)

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(3, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')
ax1.legend(loc='best')

ax2 = plt.subplot(3, 1, 2)
ax2.plot(df['CMF'])
#df['Positive'] = df['CMF'] > 0
#ax2.bar(df.index, df['CMF'], color=df.Positive.map({True: 'g', False: 'r'}))
#ax2.axhline(y=0, color='red')
ax2.grid()
ax2.set_ylabel('Chaikin Money Flow')

ax3 = plt.subplot(3, 1, 3)
df['Positive'] = df['Open'] < df['Adj Close']
colors = df.Positive.map({True: 'g', False: 'r'})
ax3.bar(df.index, df['Volume'], color=colors, alpha=0.4)
ax3.set_ylabel('Volume')
ax3.grid(True)
plt.show()

# # Candlestick with CMF
from matplotlib import dates as mdates

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
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
ax1.set_xlabel('Date')

ax2 = plt.subplot(3, 1, 2)
ax2.plot(df['CMF'])
#df['Positive'] = df['CMF'] > 0
#ax2.bar(df.index, df['CMF'], color=df.Positive.map({True: 'g', False: 'r'}))
#ax2.axhline(y=0, color='red')
ax2.grid()
ax2.set_ylabel('Chaikin Money Flow')

ax3 = plt.subplot(3, 1, 3)
df['Positive'] = df['Open'] < df['Adj Close']
colors = df.Positive.map({True: 'g', False: 'r'})
ax3.bar(df.index, df['Volume'], color=colors, alpha=0.4)
ax3.set_ylabel('Volume')
ax3.grid(True)
plt.show()