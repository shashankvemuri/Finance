#!/usr/bin/env python
# coding: utf-8

# # Stochastic RSI (STOCH RSI)

# https://www.tradingview.com/wiki/Stochastic_RSI_(STOCH_RSI)#CALCULATION
# 
# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:stochrsi

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
start = '2018-06-01'
end = '2018-12-31'

# Read data 
df = yf.download(symbol,start,end)

# View Columns
df.head()


# In[3]:


import talib as ta

df['RSI'] = ta.RSI(df['Adj Close'], timeperiod=14)
df.head(10)


# In[4]:


df = df.dropna()
df.head()


# In[5]:


LL_RSI = df['RSI'].rolling(14).min()
HH_RSI = df['RSI'].rolling(14).max()


# In[6]:


df['Stoch_RSI'] = (df['RSI'] - LL_RSI) / (HH_RSI - LL_RSI)
df = df.dropna()
df.head(10)


# In[7]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Stoch_RSI'], label='Stoch RSI')
ax2.text(s='Overbought', x=df.RSI.index[30], y=0.8, fontsize=14)
ax2.text(s='Oversold', x=df.RSI.index[30], y=0.2, fontsize=14)
ax2.axhline(y=0.8, color='red')
ax2.axhline(y=0.2, color='red')
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')


# ## Candlestick with Stoch RSI

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
ax2.plot(df['Stoch_RSI'], label='Stoch RSI')
ax2.text(s='Overbought', x=df.RSI.index[30], y=0.8, fontsize=14)
ax2.text(s='Oversold', x=df.RSI.index[30], y=0.2, fontsize=14)
ax2.axhline(y=0.8, color='red')
ax2.axhline(y=0.2, color='red')
ax2.grid()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
ax2.legend(loc='best')


# In[14]:


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
ax2.plot(df['Stoch_RSI'], label='Stoch RSI')
ax2.text(s='Overbought', x=df.RSI.index[30], y=0.8, fontsize=14)
ax2.text(s='Oversold', x=df.RSI.index[30], y=0.2, fontsize=14)
ax2.fill_between(df.index, y1=0.2, y2=0.8, color='#adccff', alpha='0.3')
ax2.axhline(y=0.8, color='red')
ax2.axhline(y=0.2, color='red')
ax2.grid(True, which='both')
ax2.minorticks_on()
ax2.set_ylabel('Volume')
ax2.set_xlabel('Date')
ax2.legend(loc='best')

