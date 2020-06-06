#!/usr/bin/env python
# coding: utf-8

# # Pretty Good Oscillator (PGO)

# https://library.tradingtechnologies.com/trade/chrt-ti-pretty-good-oscillator.html

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")


import yfinance as yf
yf.pdr_override()


# In[2]:


# input
symbol = 'AAPL'
start = '2017-01-01'
end = '2019-01-01'

# Read data 
df = yf.download(symbol,start,end)

# View Columns
df.head()


# In[3]:


n = 14
df['SMA'] = df['Adj Close'].rolling(n).mean()
df['EMA'] = df['Adj Close'].ewm(ignore_na=False,span=n,min_periods=n,adjust=True).mean()


# In[4]:


df['HL'] = df['High'] - df['Low']
df['HC'] = abs(df['High'] - df['Adj Close'].shift())
df['LC'] = abs(df['Low'] - df['Adj Close'].shift())
df['TR'] = df[['HL','HC','LC']].max(axis=1)
df['ATR'] = df['TR'].rolling(n).mean()
df = df.drop(['HL','HC','LC','TR'],axis=1)


# In[5]:


df['PGO'] = (df['Adj Close'] - df['SMA']) / df['ATR']


# In[6]:


df


# In[7]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['PGO'], label=' Pretty Good Oscillator', color='green')
ax2.axhline(y=0, color='red', linestyle='--')
ax2.grid()
ax2.set_ylabel('Pretty Good Oscillator')
ax2.set_xlabel('Date')
ax2.legend(loc='best')


# ## Candlestick with Pretty Good Oscillator (PGO)

# In[8]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].astype(dt.date))
dfc.head()


# In[9]:


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
ax2.plot(df['PGO'], label=' Pretty Good Oscillator', color='green')
ax2.axhline(y=0, color='red', linestyle='--')
ax2.grid()
ax2.set_ylabel('Pretty Good Oscillator')
ax2.set_xlabel('Date')
ax2.legend(loc='best')

