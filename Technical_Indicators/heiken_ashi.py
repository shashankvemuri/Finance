import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
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

def Heiken_Ashi(df):
    df['HA_Close']=(df['Open']+ df['High']+ df['Low']+ df['Close'])/4
    df['HA_Open']=(df['Open']+df['Close'])/2   
    
    for i in range(1, len(df)):
        df['HA_Open'][i]=(df['HA_Open'][i-1]+df['HA_Close'][i-1])/2 
    df['HA_High']=df[['HA_Open','HA_Close','High']].max(axis=1)
    df['HA_Low']=df[['HA_Open','HA_Close','Low']].min(axis=1)
    return

Heiken_Ashi(df)

HA = df[['HA_Open','HA_High','HA_Low','HA_Close', 'Volume']]

from matplotlib import dates as mdates
dfc = HA.reset_index()
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
dfc['VolumePositive'] = dfc['HA_Open'] < dfc['HA_Close']
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price (Heiken Ashi)')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.bar(dfc.index, dfc['Volume'], color=dfc.VolumePositive.map({True: 'g', False: 'r'}))
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
plt.show()

# ## Compare Heiken Ashi and Candlesticks
from matplotlib import dates as mdates

cs = df.reset_index()
cs['Date'] = mdates.date2num(cs['Date'].tolist())
cs.head()

cs = cs[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,cs.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
cs['VolumePositive'] = cs['Open'] < cs['Close']
colors = cs.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(cs.Date, cs['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*cs.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price (Candlestick)')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.bar(cs.index, cs['Volume'], color=cs.VolumePositive.map({True: 'g', False: 'r'}))
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
plt.show()

fig = plt.figure(figsize=(30,14))
ax1 = plt.subplot(2, 2, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
dfc['VolumePositive'] = dfc['HA_Open'] < dfc['HA_Close']
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price (Heiken Ashi)', fontweight="bold", fontsize=18)
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')

ax2 = plt.subplot(2, 2, 2)
candlestick_ohlc(ax2,cs.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax2.xaxis_date()
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax2.grid(True, which='both')
ax2.minorticks_on()
ax2v = ax2.twinx()
cs['VolumePositive'] = cs['Open'] < cs['Close']
colors = cs.VolumePositive.map({True: 'g', False: 'r'})
ax2v.bar(cs.Date, cs['Volume'], color=colors, alpha=0.4)
ax2v.axes.yaxis.set_ticklabels([])
ax2v.set_ylim(0, 3*cs.Volume.max())
ax2.set_title('Stock '+ symbol +' Closing Price (Candlestick)', fontweight="bold", fontsize=18)
ax2.set_ylabel('Price')
ax2.set_xlabel('Date')
plt.show()