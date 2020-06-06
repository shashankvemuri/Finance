#!/usr/bin/env python
# coding: utf-8

# # Volume Accumulation Oscillator (VAO)

# Volume Accumulation Oscillator (VAO) use for volume times the difference of the current price and the midpoint price. As a result, is used as a divergence indicator with the high and low price. 
# 
# https://www.marketvolume.com/technicalanalysis/vao.asp

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

# Create Volume Accumulation Oscillator (VAO) indicator
df['VAO'] = df['Volume'] * (df['Adj Close'] - (df['High']+df['Low'])/2)
df.head()


# In[4]:


df['Positive'] = df['VAO'] > 0


# In[5]:


df['VolumePositive'] = df['Open'] < df['Adj Close']


# In[6]:


df.head()


# In[12]:


# Line Chart
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df.index, df['Adj Close'])
ax1.axhline(y=df['Adj Close'].mean(),color='r')
ax1.grid()
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.bar(df.index, df['VAO'], color=df.Positive.map({True: 'g', False: 'r'}))
ax2.grid()
ax2.set_ylabel('VAO')
ax2.set_xlabel('Date')


# In[8]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df.index, df['Adj Close'])
ax1.axhline(y=df['Adj Close'].mean(),color='r')
ax1.grid()
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df.index, df['VAO'])
ax2.grid()
ax2.set_ylabel('VAO')
ax2.set_xlabel('Date')


# ## Candlestick with VAO

# In[9]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df.copy()
dfc['VAO'] = dfc['Volume'] * (dfc['Adj Close'] - (dfc['High']+dfc['Low'])/2)
dfc['Positive'] = dfc['VAO'] > 0
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].astype(dt.date))
dfc.head()


# In[13]:


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
ax2.bar(dfc.Date, dfc['VAO'], color=dfc.Positive.map({True: 'g', False: 'r'}))
ax2.grid()
ax2.set_ylabel('VAO')
ax2.set_xlabel('Date')


# In[17]:


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
ax2.fill_between(dfc.Date, dfc['VAO'],where= dfc['VAO'] >= 0,
                 facecolor='green', interpolate=True)
ax2.fill_between(dfc.Date, dfc['VAO'],where= dfc['VAO'] <= 0,
                 facecolor='red', interpolate=True)
ax2.grid()
ax2.set_ylabel('VAO')
ax2.set_xlabel('Date')

