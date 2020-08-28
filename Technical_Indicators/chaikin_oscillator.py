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
start = dt.date.today() - dt.timedelta(days = 356*3)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

df['MF_Multiplier'] = (2*df['Adj Close']-df['Low']-df['High'])/(df['High']-df['Low'])
df['MF_Volume'] = df['MF_Multiplier']*df['Volume']
df['ADL'] = df['MF_Volume'].cumsum()
df = df.drop(['MF_Multiplier','MF_Volume'],axis=1)

df['ADL_3_EMA'] = df['ADL'].ewm(ignore_na=False,span=3,min_periods=2,adjust=True).mean()
df['ADL_10_EMA'] = df['ADL'].ewm(ignore_na=False,span=10,min_periods=9,adjust=True).mean()
df['Chaikin_Oscillator'] = df['ADL_3_EMA'] - df['ADL_10_EMA']
df = df.drop(['ADL','ADL_3_EMA','ADL_10_EMA'],axis=1)

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Chaikin_Oscillator'], label='Chaikin Oscillator', color='black')
ax2.axhline(y=0, color='darkblue')
ax2.text(s='Positive', x=df.index[0], y=1, verticalalignment='bottom', fontsize=14, color='green')
ax2.text(s='Negative', x=df.index[0], y=1, verticalalignment='top', fontsize=14, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Chaikin Oscillator')
ax2.set_xlabel('Date')
plt.show()

# ## Candlestick with Chaikin Oscillator
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
ax2.plot(df['Chaikin_Oscillator'], label='Chaikin Oscillator', color='black')
ax2.axhline(y=0, color='darkblue')
ax2.text(s='Positive', x=dfc.Date[0], y=1, verticalalignment='bottom', fontsize=14, color='green')
ax2.text(s='Negative', x=dfc.Date[0], y=1, verticalalignment='top', fontsize=14, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Chaikin Oscillator')
ax2.set_xlabel('Date')
plt.show()