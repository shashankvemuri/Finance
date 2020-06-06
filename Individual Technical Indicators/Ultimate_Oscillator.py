#!/usr/bin/env python
# coding: utf-8

# # Ultimate Oscillator

# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ultimate_oscillator

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


df['Prior Close'] = df['Adj Close'].shift()
df['BP'] = df['Adj Close'] - df[['Low','Prior Close']].min(axis=1)
df['TR'] = df[['High','Prior Close']].max(axis=1) - df[['Low','Prior Close']].min(axis=1)
df['Average7'] = df['BP'].rolling(7).sum()/df['TR'].rolling(7).sum()
df['Average14'] = df['BP'].rolling(14).sum()/df['TR'].rolling(14).sum()
df['Average28'] = df['BP'].rolling(28).sum()/df['TR'].rolling(28).sum()
df['UO'] = 100 * (4*df['Average7']+2*df['Average14']+df['Average28'])/(4+2+1)
df = df.drop(['Prior Close','BP','TR','Average7','Average14','Average28'],axis=1)


# In[4]:


df.head(30)


# In[5]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['UO'], label='Ultimate Oscillator')
#ax2.axhline(y=70, color='red')
#ax2.axhline(y=50, color='black', linestyle='--')
#ax2.axhline(y=30, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Ultimate Oscillator')
ax2.set_xlabel('Date')


# ## Candlestick with Ultimate Oscillator

# In[6]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].astype(dt.date))
dfc.head()


# In[7]:


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
ax2.plot(df['UO'], label='Ultimate Oscillator')
#ax2.axhline(y=70, color='red')
#ax2.axhline(y=50, color='black', linestyle='--')
#ax2.axhline(y=30, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Ultimate Oscillator')
ax2.set_xlabel('Date')

