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

n = 14 # Number of days
df['Prior Low'] = df['Low'].shift()
df['Prior High'] = df['High'].shift()
df['+VM'] = abs(df['High'] - df['Prior Low'])
df['-VM'] = abs(df['Low'] - df['Prior High'])
df['+VM_'+str(n)] = df['+VM'].rolling(n).sum()
df['-VM_'+str(n)] = df['-VM'].rolling(n).sum()
df['HL'] = df['High'] - df['Low']
df['HC'] = abs(df['High'] - df['Adj Close'].shift())
df['LC'] = abs(df['Low'] -df['Adj Close'].shift())
df['TR'] = df[['HL','HC','LC']].max(axis=1)

del df['HL']
del df['HC']
del df['LC']

df['TR_'+str(n)] = df['TR'].rolling(n).sum()
df['+VI_'+str(n)] = df['+VM_'+str(n)]/df['TR_'+str(n)]
df['-VI_'+str(n)] = df['-VM_'+str(n)]/df['TR_'+str(n)]


df = df.drop(['Prior Low','Prior High','+VM','-VM','+VM_14','-VM_14','TR','TR_14'],axis=1)

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['+VI_14'], label='+VI', color='g')
ax2.plot(df['-VI_14'], label='-VI', color='r')
ax2.axhline(y=1, color='black')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Vortex Indicator')
ax2.set_xlabel('Date')
plt.show()

# ## Candlestick with Vortex Indicator
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
ax2.plot(df['+VI_14'], label='+VI', color='g')
ax2.plot(df['-VI_14'], label='-VI', color='r')
ax2.axhline(y=1, color='black')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Vortex Indicator')
ax2.set_xlabel('Date')
plt.show()