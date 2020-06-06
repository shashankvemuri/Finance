#!/usr/bin/env python
# coding: utf-8

# # Kaufman's Adaptive Moving Average (KAMA)

# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:kaufman_s_adaptive_moving_average

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


n = 10
df['Change'] = abs(df['Adj Close'] - df['Adj Close'].shift(10))
df['Volatility'] = abs(df['Adj Close'] - df['Adj Close'].shift()).rolling(n).sum()
df['ER'] = df['Change']/df['Volatility']
df['SC'] = np.square(df['ER']*(2.0/(2+1)-2.0/(30+1))+2.0/(30+1))
df['KAMA'] = df['Adj Close'].rolling(n).mean()
df['KAMA'][:n]= np.nan


# In[4]:


i = 1
while i<len(df['KAMA'][n+1:]):
        s = df['KAMA']
        s.iloc[n+i] = df['KAMA'][n+i-1] + df['SC'][n+i]*(df['Adj Close'][n+i] - df['KAMA'][n+i-1])
        df['KAMA'] = s
        i = i + 1
df = df.drop(['Change','Volatility','ER','SC'],axis=1)


# In[5]:


df.head(20)


# In[6]:


plt.figure(figsize=(14,10))
plt.plot(df['Adj Close'])
plt.plot(df['KAMA'])
plt.ylabel('Price')
plt.xlabel('Date')
plt.title('Stock Closing Price of ' + str(n) + '-Day KAMA')
plt.legend(loc='best')


# ## Candlestick with KAMA

# In[7]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].astype(dt.date))
dfc.head()


# In[8]:


from mplfinance.original_flavor import candlestick_ohlc

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df['KAMA'], label='KAMA')
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

