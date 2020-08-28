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

# Create a function for Ease of Movement
def EVM(data, ndays): 
    dm = ((data['High'] + data['Low'])/2) - ((data['High'].shift(1) + data['Low'].shift(1))/2)
    br = (data['Volume'] / 100000000) / ((data['High'] - data['Low']))
    EVM = dm / br 
    EVM_MA = pd.Series(EVM.rolling(ndays).mean(), name='EVM')
    data = data.join(EVM_MA) 
    return data

# Compute the 14-day Ease of Movement for stock
n = 14
Stock_EVM = EVM(df, n)
EVM = Stock_EVM['EVM']

# Plotting the Price Series chart and the Ease Of Movement below
fig = plt.figure(figsize=(16,12))
ax = fig.add_subplot(2, 1, 1)
ax.set_xticklabels([])
ax.plot(df['Adj Close'],lw=1)
ax.axhline(y=df['Adj Close'].mean(),color='r')
ax.set_title(symbol + ' Price Chart')
ax.set_ylabel('Close Price')
ax.grid(True)

ax1 = fig.add_subplot(2, 1, 2)
ax1.plot(EVM,'k',lw=0.75,linestyle='-',label='EVM(14)')
ax1.axhline(y=0,color='r')
ax1.legend(loc=2,prop={'size':9})
ax1.set_ylabel('EVM values')
ax1.grid(True)
ax1 = plt.gca()
ax1.get_xticklabels()


# ## Candlestick with EVM
from matplotlib import dates as mdates
dfc = df.copy()
dfc = dfc.dropna()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
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
ax1v.fill_between(dfc.Date, 0, dfc.Volume[0:], facecolor='#0079a3', alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(EVM, label='EVM')
ax2.axhline(y=0,color='r')
ax2.grid()
ax2.set_ylabel('Ease of Movement')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()


# ## Candlestick with Ease of Movement
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
ax2.plot(EVM, label='EVM')
ax2.axhline(y=0,color='r')
ax2.grid()
ax2.set_ylabel('Ease of Movement')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()