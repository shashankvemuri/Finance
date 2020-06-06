#!/usr/bin/env python
# coding: utf-8

# # Price Relative

# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:price_relative

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
symbol1 = 'AAPL'
symbol2 = '^GSPC'
start = '2018-10-01'
end = '2019-01-01'

# Read data 
df1 = yf.download(symbol1,start,end)
df2 = yf.download(symbol2,start,end)


# In[3]:


df = pd.concat([df1['Adj Close'], df2['Adj Close']],axis=1)


# In[4]:


# Rename columns
df.columns = [symbol1,symbol2]


# In[5]:


df['Price Relative'] = df['AAPL']/df['^GSPC']
df['Percentage Change in Price Relative'] = ((df['Price Relative']-df['Price Relative'].shift())/df['Price Relative'].shift())*100


# In[6]:


df.head()


# In[7]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df1['Adj Close'])
ax1.set_title('Stock '+ symbol1 +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Percentage Change in Price Relative'], label='Price Relative', color='black')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Price Relative')
ax2.set_xlabel('Date')


# ## Candlestick with Price Relative

# In[8]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df1.copy()
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
ax1v.set_ylim(0, 3*df1.Volume.max())
ax1.set_title('Stock '+ symbol1 +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['Percentage Change in Price Relative'], label='Price Relative', color='black')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Price Relative')
ax2.set_xlabel('Date')

