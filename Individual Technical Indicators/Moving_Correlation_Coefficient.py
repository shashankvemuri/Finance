#!/usr/bin/env python
# coding: utf-8

# # Moving Correlation Coefficient

# https://www.fmlabs.com/reference/default.htm

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
symbol2 = 'QQQ'
start = '2017-01-01'
end = '2019-01-01'

# Read data 
df1 = yf.download(symbol1,start,end)
df2 = yf.download(symbol2,start,end)

# View Columns
df1.head()


# In[3]:


df2.head()


# In[4]:


cc = df1['Adj Close'].corr(df2['Adj Close'])


# In[5]:


cc


# In[6]:


df = pd.concat([df1['Adj Close'], df2['Adj Close']],axis=1)


# In[7]:


df.head()


# In[8]:


# Rename columns
df.columns = [symbol1,symbol2]


# In[9]:


df.head()


# In[10]:


n = 14
df['M_Cor'] = df['AAPL'].rolling(n).corr(df['QQQ']).rolling(n).mean()


# In[11]:


df.head(30)


# In[12]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df1['Adj Close'])
ax1.set_title('Stock '+ symbol1 +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['M_Cor'], label='Moving Correlation Coefficient', color='black')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Moving Correlation Coefficient')
ax2.set_xlabel('Date')


# ## Candlestick with Moving Correlation Coefficient

# In[13]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df1.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].astype(dt.date))
dfc.head()


# In[14]:


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
ax2.plot(df['M_Cor'], label='Moving Correlation Coefficient', color='black')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Moving Correlation Coefficient')
ax2.set_xlabel('Date')

