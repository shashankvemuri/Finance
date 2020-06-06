#!/usr/bin/env python
# coding: utf-8

# # Moving Average Envelopes

# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_average_envelopes

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
start = '2018-01-01'
end = '2019-01-01'

# Read data 
df = yf.download(symbol,start,end)

# View Columns
df.head()


# In[3]:


import talib as ta


# In[4]:


df['20SMA'] = ta.SMA(df['Adj Close'], timeperiod=20)


# In[5]:


df['Upper_Envelope'] = df['20SMA'] + (df['20SMA'] * 0.025)
df['Lower_Envelope'] = df['20SMA'] - (df['20SMA'] * 0.025)


# In[6]:


df.head()


# In[7]:


# Line Chart
plt.figure(figsize=(14,8))
plt.plot(df['Adj Close'])
plt.plot(df['Upper_Envelope'], color='blue')
plt.plot(df['Lower_Envelope'], color='red')
plt.plot(df['Adj Close'].rolling(20).mean(), color='orange', label='Average Price', linestyle='--')
plt.title('Stock of Moving Average Envelopes')
plt.ylabel('Price')
plt.xlabel('Date')
plt.legend(loc='best')
plt.show()


# ## Candlestick with MAE

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

fig = plt.figure(figsize=(18,8))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df['Upper_Envelope'], color='blue')
ax1.plot(df['Lower_Envelope'], color='red')
ax1.plot(df['Adj Close'].rolling(20).mean(), color='orange')
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

