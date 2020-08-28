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
start = dt.date.today() - dt.timedelta(days = 365*2)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

n = 7 # Number of periods
df['H-L'] = abs(df['High']-df['Low'])
df['H-PC'] = abs(df['High']-df['Close'].shift(1))
df['L-PC'] = abs(df['Low']-df['Close'].shift(1))
df['TR'] = df[['H-L','H-PC','L-PC']].max(axis=1)
df['ATR'] = np.nan
df.ix[n-1,'ATR'] = df['TR'][:n-1].mean()
for i in range(n,len(df)):
    df['ATR'][i]=(df['ATR'][i-1]*(n-1)+ df['TR'][i])/n


f = 3 # Number of factor
# BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
# BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR
df['BASIC UPPERBAND']=(df['High']+df['Low'])/2+(f*df['ATR'])
df['BASIC LOWERBAND']=(df['High']+df['Low'])/2-(f*df['ATR'])
df['FINAL UPPERBAND']=df['BASIC UPPERBAND']
df['FINAL LOWERBAND']=df['BASIC LOWERBAND']


# FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) 
# and (Previous Close > Previous FINAL UPPERBAND)) 
# THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
for i in range(n,len(df)):
    if df['Close'][i-1]<=df['FINAL UPPERBAND'][i-1]:
        df['FINAL UPPERBAND'][i]=min(df['BASIC UPPERBAND'][i],df['FINAL UPPERBAND'][i-1])
    else:
        df['FINAL UPPERBAND'][i]=df['BASIC UPPERBAND'][i]    

# FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) 
# and (Previous Close < Previous FINAL LOWERBAND)) 
# THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)
for i in range(n,len(df)):
    if df['Close'][i-1]>=df['BASIC LOWERBAND'][i-1]:
        df['FINAL LOWERBAND'][i]=max(df['BASIC LOWERBAND'][i],df['FINAL LOWERBAND'][i-1])
    else:
        df['FINAL LOWERBAND'][i]=df['BASIC LOWERBAND'][i]   
        
# SUPERTREND = IF(Current Close <= Current FINAL UPPERBAND) 
# THEN Current FINAL UPPERBAND ELSE Current  FINAL LOWERBAND
df['SUPERTREND']=np.nan
for i in df['SUPERTREND']:
    if df['Close'][n-1]<=df['FINAL UPPERBAND'][n-1]:
        df['SUPERTREND'][n-1]=df['FINAL UPPERBAND'][n-1]
    elif df['Close'][n-1]>df['FINAL UPPERBAND'][i]:
        df['SUPERTREND'][n-1]=df['FINAL LOWERBAND '][n-1]

for i in range(n,len(df)):
    if df['SUPERTREND'][i-1]==df['FINAL UPPERBAND'][i-1] and df['Close'][i]<=df['FINAL UPPERBAND'][i]:
        df['SUPERTREND'][i]=df['FINAL UPPERBAND'][i]
    elif df['SUPERTREND'][i-1]==df['FINAL UPPERBAND'][i-1] and df['Close'][i]>=df['FINAL UPPERBAND'][i]:
        df['SUPERTREND'][i]=df['FINAL LOWERBAND'][i]
    elif df['SUPERTREND'][i-1]==df['FINAL LOWERBAND'][i-1] and df['Close'][i]>=df['FINAL LOWERBAND'][i]:
        df['SUPERTREND'][i]=df['FINAL LOWERBAND'][i]
    elif df['SUPERTREND'][i-1]==df['FINAL LOWERBAND'][i-1] and df['Close'][i]<=df['FINAL LOWERBAND'][i]:
        df['SUPERTREND'][i]=df['FINAL UPPERBAND'][i]

plt.figure(figsize=(14,7))

df['Adj Close'].plot()
df['SUPERTREND'].plot()
plt.title('Stock of SuperTrend', fontsize=18)
plt.legend(loc='best')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# ## Candlestick with SuperTrend
from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())

from mplfinance.original_flavor import candlestick_ohlc
plt.style.use('fivethirtyeight')
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.plot(df['SUPERTREND'])
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
ax1.set_xlabel('Date')
ax1.legend()
plt.show()