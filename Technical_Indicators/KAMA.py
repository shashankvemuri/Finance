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

n = 10
df['Change'] = abs(df['Adj Close'] - df['Adj Close'].shift(10))
df['Volatility'] = abs(df['Adj Close'] - df['Adj Close'].shift()).rolling(n).sum()
df['ER'] = df['Change']/df['Volatility']
df['SC'] = np.square(df['ER']*(2.0/(2+1)-2.0/(30+1))+2.0/(30+1))
df['KAMA'] = df['Adj Close'].rolling(n).mean()
df['KAMA'][:n]= np.nan

i = 1
while i<len(df['KAMA'][n+1:]):
        s = df['KAMA']
        s.iloc[n+i] = df['KAMA'][n+i-1] + df['SC'][n+i]*(df['Adj Close'][n+i] - df['KAMA'][n+i-1])
        df['KAMA'] = s
        i = i + 1
df = df.drop(['Change','Volatility','ER','SC'],axis=1)

plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
plt.plot(df['KAMA'])
plt.ylabel('Price')
plt.xlabel('Date')
plt.title('Stock Closing Price of ' + str(n) + '-Day KAMA')
plt.legend(loc='best')
plt.show()

# ## Candlestick with KAMA
from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
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
plt.show()