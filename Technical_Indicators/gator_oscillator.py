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
start = dt.date.today() - dt.timedelta(days = 365*4)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

def SMMA(price, n, m=3):
    SMMA = np.array([np.nan] * len(price))
    SMMA[n - 2] = price[:n - 1].mean()
    for i in range(n - 1, len(price)):
        SMMA[i] = (SMMA [i - 1] * (n - 2) + 2 * price[i]) / n
    return SMMA

medianprice = (df['High']/2) + (df['Low']/2)
df['Jaw'] = SMMA(medianprice,13,8)
df['Teeth'] = SMMA(medianprice,8 ,5)
df['Lips']  = SMMA(medianprice,5 ,3) 

df['Top_Bars'] = abs(df['Jaw'] - df['Teeth'])
df['Bottom_Bars'] = -(abs(df['Teeth'] - df['Lips']))

fig = plt.figure(figsize=(14,7))

ax1 = fig.add_subplot(2, 1, 1)
ax1.plot(df['Adj Close'],lw=1)
ax1.plot(df['Jaw'],color='blue')
ax1.plot(df['Teeth'],color='red')
ax1.plot(df['Lips'],color='green')
ax1.set_title(symbol + ' Close Price')
ax1.set_ylabel('Stock price')
ax1.set_xlabel('Date')
ax1.grid(True)
ax1.legend(loc='best')

ax2 = fig.add_subplot(2, 1, 2)
df['Positive_T'] = df.Top_Bars > df.Top_Bars.shift(1)
df['Positive_B'] = df.Bottom_Bars > df.Bottom_Bars.shift(1)
ax2.bar(df.index, df['Top_Bars'], color=df.Positive_T.map({True: 'g', False: 'r'}), label='Top')
ax2.bar(df.index, df['Bottom_Bars'], color=df.Positive_B.map({True: 'g', False: 'r'}), label='Bottom')
#ax2.bar(df.index, df['Top_Bars'],label='Top')
#ax2.bar(df.index, df['Bottom_Bars'],label='Bottom')
ax2.legend(loc=2,prop={'size':8})
ax2.grid(True)
plt.show()


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
ax1.plot(df['Jaw'],color='blue')
ax1.plot(df['Teeth'],color='red')
ax1.plot(df['Lips'],color='green')
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
ax1.legend(loc='best')

ax2 = fig.add_subplot(2, 1, 2)
df['Positive_T'] = df.Top_Bars > df.Top_Bars.shift(1)
df['Positive_B'] = df.Bottom_Bars > df.Bottom_Bars.shift(1)
ax2.bar(df.index, df['Top_Bars'], color=df.Positive_T.map({True: 'g', False: 'r'}), label='Top')
ax2.bar(df.index, df['Bottom_Bars'], color=df.Positive_B.map({True: 'g', False: 'r'}), label='Bottom')
ax2.legend(loc=2,prop={'size':8})
ax2.grid(True)
plt.show()