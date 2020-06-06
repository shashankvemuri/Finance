#!/usr/bin/env python
# coding: utf-8

# # Inverse Fisher Transform

# https://www.motivewave.com/studies/inverse_fisher_transform.htm
# 
# https://www.metastock.com/customer/resources/tasc/?id=60
# 
# https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf

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


v1 = 0.1 * (ta.RSI(df['Adj Close'], timeperiod=5) - 50)
v2 = ta.WMA(v1, timeperiod=9)


# In[5]:


df['IFT'] = pd.Series((np.exp(2 * v2) - 1) / (np.exp(2 * v2) + 1))


# In[6]:


df.head(20)


# In[7]:


fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['IFT'], label='Inverse Fisher Transform', color='red')
#ax2.axhline(y=0, color='blue', linestyle='--')
ax2.axhline(y=0.5, color='darkblue')
ax2.axhline(y=-0.5, color='darkblue')
ax2.grid()
ax2.set_ylabel('Inverse Fisher Transform')
ax2.set_xlabel('Date')
ax2.legend(loc='best')


# ## Candlestick with Inverse Fisher Transform

# In[8]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = pd.to_datetime(dfc['Date'])
dfc['Date'] = dfc['Date'].apply(mdates.date2num)
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
ax2.plot(df['IFT'], label='Inverse Fisher Transform', color='red')
ax2.axhline(y=0.5, color='darkblue')
ax2.axhline(y=-0.5, color='darkblue')
ax2.grid()
ax2.set_ylabel('Inverse Fisher Transform')
ax2.set_xlabel('Date')
ax2.legend(loc='best')

