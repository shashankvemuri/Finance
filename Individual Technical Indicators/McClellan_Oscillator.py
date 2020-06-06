#!/usr/bin/env python
# coding: utf-8

# # McClellan Oscillator

# https://stockcharts.com/school/doku.php?id=chart_school:market_indicators:mcclellan_oscillator
# 
# Market Indicator

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
dfs = yf.download(symbol,start,end)

# View Columns
dfs.head()


# In[3]:


import talib as ta


# https://en.wikipedia.org/wiki/Advance%E2%80%93decline_line
# 
# https://www.investopedia.com/terms/m/mcclellanoscillator.asp

# In[4]:


change = dfs['Adj Close'].diff()
Advances = change[change > 0]  
Declines = change[change <= 0]


# In[5]:


# df[['Advances', 'Declines']] = df[['Advances', 'Declines']].fillna(0)
# df['ADL'] = df['Advances'].fillna(df['Declines'])
# ADL for stocks
dfs['ADL_Stock'] = Advances.combine_first(Declines)


# In[6]:


dfs.head()


# https://stockcharts.com/school/doku.php?id=chart_school:market_indicators:mcclellan_oscillator

# In[7]:


import quandl as q

Advances = q.get('URC/NYSE_ADV', start_date = "2018-01-01")['Numbers of Stocks']
Declines = q.get('URC/NYSE_DEC', start_date = "2018-01-01")['Numbers of Stocks'] 


# In[8]:


df = pd.DataFrame()
df['Advances'] = Advances
df['Declines'] = Declines
df.head()


# In[9]:


#Ratio Adjusted Net Advances (RANA): (Advances - Declines)/(Advances + Declines)  
#RANA = (advances - declines) / (advances + declines)  
# df['Net_Advances'] = df['Advances'] - df['Declines']
# df['Ratio_Adjusted'] = (df['Net_Advances']/(df['Advances'] + df['Declines']))*1000
df['Net_Advances'] = df['Advances'] - df['Declines'] 
df['Ratio_Adjusted'] = (df['Net_Advances']/(df['Advances'] + df['Declines'])) * 1000
df['19_EMA'] = ta.EMA(df['Ratio_Adjusted'], timeperiod=19)
df['39_EMA'] = ta.EMA(df['Ratio_Adjusted'], timeperiod=39)
df['RANA'] = (df['Advances'] - df['Declines']) / (df['Advances'] + df['Declines']) * 1000


# In[10]:


df.tail(20)


# In[11]:


plt.figure(figsize=(12,6))
plt.plot(dfs.index, dfs['Adj Close'])
plt.axhline(y=dfs['Adj Close'].mean(),color='r')
plt.title('Stock Close Price')
plt.grid()
plt.ylabel('Price')
plt.show()


# ## Comparing Stock and McClellan Oscillator

# In[12]:


# Line Chart
# See if the stock correlate with Market Indicator
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(dfs.index, dfs['Adj Close'])
ax1.axhline(y=dfs['Adj Close'].mean(),color='r')
ax1.grid()
ax1.set_ylabel('Price')

df['Positive'] = df['RANA'] > 0
ax2 = plt.subplot(2, 1, 2)
ax2.bar(df.index, df['RANA'], color=df.Positive.map({True: 'g', False: 'r'}))
ax2.grid()
ax2.set_ylabel('Ratio Adjusted Net Advances')
ax2.set_xlabel('Date')


# ## NYSE Advance and Declines

# In[13]:


fig = plt.figure(figsize=(14,7))
df['Positive'] = df['RANA'] > 0
ax = plt.subplot(2, 1, 1)
ax.bar(df.index, df['RANA'], color=df.Positive.map({True: 'g', False: 'r'}))
ax.grid()
ax.set_ylabel('Ratio Adjusted Net Advances')
ax.set_xlabel('Date')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df.index, df['19_EMA'], color='b', label='19-day EMA')
ax2.plot(df.index, df['39_EMA'], color='r', label='39-day EMA')
ax2.grid()
ax2.set_ylabel('Ratio Adjusted Net Advances')
ax2.legend(loc='best')
ax2.set_xlabel('Date')

