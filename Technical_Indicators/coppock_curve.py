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

n = [11,14]
for nd in n:
  df['ROC_'+str(nd)] = ((df['Adj Close'] - df['Adj Close'].shift(nd))/df['Adj Close'].shift(nd)) * 100

df['COPP'] = (df['ROC_14']+df['ROC_11']).ewm(ignore_na=False,span=10,min_periods=10,adjust=True).mean()

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(4, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(4, 1, 2)
ax2.plot(df['COPP'], label='Coppock Curve', color='black')
ax2.axhline(y=0, color='red')
ax2.grid()
ax2.set_ylabel('Coppock Curve')
ax2.legend(loc='best')

ax3 = plt.subplot(4, 1, 3)
ax3.plot(df['ROC_11'], label='ROC 11', color='black')
ax3.axhline(y=0, color='red')
ax3.grid()
ax3.set_ylabel('11 Month Rate-of-Change')
ax3.legend(loc='best')

ax4 = plt.subplot(4, 1, 4)
ax4.plot(df['ROC_14'], label='ROC 14', color='black')
ax4.axhline(y=0, color='red')
ax4.grid()
ax4.set_ylabel('14 Month Rate-of-Change')
ax4.legend(loc='best')
plt.show()

# ## Candlestick with Coppock Curve
from matplotlib import dates as mdates

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(4, 1, 1)
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

ax2 = plt.subplot(4, 1, 2)
ax2.plot(df['COPP'], label='Coppock Curve', color='black')
ax2.axhline(y=0, color='red')
ax2.grid()
ax2.set_ylabel('Coppock Curve')
ax2.legend(loc='best')

ax3 = plt.subplot(4, 1, 3)
ax3.plot(df['ROC_11'], label='ROC 11', color='black')
ax3.axhline(y=0, color='red')
ax3.grid()
ax3.set_ylabel('11 Month Rate-of-Change')
ax3.legend(loc='best')

ax4 = plt.subplot(4, 1, 4)
ax4.plot(df['ROC_14'], label='ROC 14', color='black')
ax4.axhline(y=0, color='red')
ax4.grid()
ax4.set_ylabel('14 Month Rate-of-Change')
ax4.legend(loc='best')
plt.show()