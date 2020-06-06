#!/usr/bin/env python
# coding: utf-8

# # Ulcer Index

# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ulcer_index

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
df[str(n)+'-period Max Close'] = df['Adj Close'].rolling(n).max()
df['Percent_Drawdown'] = 100* (df['Adj Close'] - df[str(n)+'-period Max Close'])/df[str(n)+'-period Max Close']
df['Percent_Drawdown_Squared'] = df['Percent_Drawdown'] ** 2
df['Squared_Average'] = df['Percent_Drawdown_Squared'].rolling(n).sum()/14
df['Ulcer_Index'] = df['Squared_Average'].pow(0.5)
df = df.drop([str(n)+'-period Max Close','Percent_Drawdown','Percent_Drawdown_Squared','Squared_Average'],axis=1)


# In[4]:


df.head(20)


# In[5]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Ulcer_Index'], label='Ulcer Index')
# ax2.axhline(y=0, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Ulcer Index')
ax2.set_xlabel('Date')


# ## Candlestick with Ulcer Index

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
ax2.plot(df['Ulcer_Index'], label='Ulcer Index')
# ax2.axhline(y=0, color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Ulcer Index')
ax2.set_xlabel('Date')

