import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'SPY'
start = dt.date.today() - dt.timedelta(days = 365*7)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

new_high = df['Adj Close'].rolling(52).max() # 52-week lows
new_low = df['Adj Close'].rolling(52).min() # 52-week highs

print("Yesterday's Value:", df['Adj Close'][-2]) # Yesterday's Value
print("Current Value:", df['Adj Close'][-1]) # Current's Value

new_high = new_high.dropna()
new_low = new_low.dropna()
#Record_High_Percent = (new_high /(new_high + new_low)) * 100
#nhnl = new_high - new_low

# 1. Cumulative New High/Low Line
# Today's Value = Yesterday's Value + (Today's New Highs - Today's New Lows) 
df['CNHL'] = df['Adj Close'][1] + (new_high - new_low)

# 2. New-High Minus New-Low Oscillator 
# Oscillator = Today\'s New Highs – Today\'s New Lows
df['Oscillator'] = new_high - new_low

# 3. New High/Low Ratio
# Ratio = Today\'s New Highs / Today\'s New Lows 
df['Ratio'] = new_high / new_low

# 4. Percentage of New-High to New High + New Low 
# % New Highs = Today\'s New Highs / (Today\'s New Highs + Today\'s New Lows) 
# % New Lows = Today\'s New Lows / (Today\'s New Highs + Today\'s New Lows) 
df['NH'] = new_high/ (new_high + new_low)
df['NL'] = new_high/ (new_high + new_low)

# 5. Percentage of New Highs to Total Market 
# % New Highs = Today\'s New Highs / Total # of Listed Stocks in Given Market 
# % New Lows = Today\'s New Lows / Total # of Listed Stocks in Given Market 
df['NHTM'] = new_high / 5 # Number of stocks
df['NLTM'] = new_low / 5 # Number of stocks

df = df.dropna()

fig = plt.figure(figsize=(14,14))
ax1 = plt.subplot(3, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(3, 1, 2)
ax2.plot(df['CNHL'], label='Cumulative New High/Low Line')
#ax2.axhline(y=0, color='red')
ax2.set_ylabel('Cumulative New High/Low Line')
ax2.grid()

ax3 = plt.subplot(3, 1, 3)
ax3.plot(df['Oscillator'], label='Oscillator')
#ax3.axhline(y=50, color='red')
ax3.set_ylabel('Oscillator')
ax3.set_xlabel('Date')
ax3.grid()
plt.show()

# ## Candlestick with New Highs/New Lows
from matplotlib import dates as mdates
df['VolumePositive'] = df['Open'] < df['Adj Close']
df = df.dropna()
df = df.reset_index()
df['Date'] = mdates.date2num(df['Date'].tolist())

from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(16,8))
ax1 = plt.subplot(3, 1, 1)
candlestick_ohlc(ax1,df.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1v = ax1.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(df.Date, df['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(3, 1, 2)
ax2.plot(df['CNHL'], label='Cumulative New High/Low Line')
#ax2.axhline(y=0, color='red')
ax2.grid()
ax2.set_ylabel('Cumulative New High/Low Line')

ax3 = plt.subplot(3, 1, 3)
ax3.plot(df['Oscillator'], label='Oscillator')
#ax3.axhline(y=50, color='red')
ax3.grid()
ax3.set_ylabel('Oscillator')
ax3.set_xlabel('Date')
plt.show()