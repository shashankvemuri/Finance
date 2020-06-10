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
start = dt.date.today() - dt.timedelta(days = 180)
end = dt.date.today()

# Read data 
dfs = yf.download(symbol,start,end)

import talib as ta

change = dfs['Adj Close'].diff()
Advances = change[change > 0]  
Declines = change[change <= 0]

# df[['Advances', 'Declines']] = df[['Advances', 'Declines']].fillna(0)
# df['ADL'] = df['Advances'].fillna(df['Declines'])
# ADL for stocks
dfs['ADL_Stock'] = Advances.combine_first(Declines)

import quandl as q

Advances = q.get('URC/NYSE_ADV', start_date = "2018-01-01")['Numbers of Stocks']
Declines = q.get('URC/NYSE_DEC', start_date = "2018-01-01")['Numbers of Stocks'] 

df = pd.DataFrame()
df['Advances'] = Advances
df['Declines'] = Declines
df.head()

#Ratio Adjusted Net Advances (RANA): (Advances - Declines)/(Advances + Declines)  
#RANA = (advances - declines) / (advances + declines)  
# df['Net_Advances'] = df['Advances'] - df['Declines']
# df['Ratio_Adjusted'] = (df['Net_Advances']/(df['Advances'] + df['Declines']))*1000
df['Net_Advances'] = df['Advances'] - df['Declines'] 
df['Ratio_Adjusted'] = (df['Net_Advances']/(df['Advances'] + df['Declines'])) * 1000
df['19_EMA'] = ta.EMA(df['Ratio_Adjusted'], timeperiod=19)
df['39_EMA'] = ta.EMA(df['Ratio_Adjusted'], timeperiod=39)
df['RANA'] = (df['Advances'] - df['Declines']) / (df['Advances'] + df['Declines']) * 1000

plt.figure(figsize=(12,6))
plt.plot(dfs.index, dfs['Adj Close'])
plt.axhline(y=dfs['Adj Close'].mean(),color='r')
plt.title('Stock Close Price')
plt.grid()
plt.ylabel('Price')
plt.show()

# ## Comparing Stock and McClellan Oscillator
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
plt.show()

# ## NYSE Advance and Declines
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
plt.show()