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

returns = df['Adj Close'].pct_change()
vol_decrease = (df['Volume'].shift(1) > df['Volume'])

nvi = pd.Series(data=np.nan, index=df['Adj Close'].index, dtype='float64')

nvi.iloc[0] = 1000
for i in range(1,len(nvi)):
    if vol_decrease.iloc[i]:
        nvi.iloc[i] = nvi.iloc[i - 1] * (1.0 + returns.iloc[i])
    else:
        nvi.iloc[i] = nvi.iloc[i - 1]

nvi = nvi.replace([np.inf, -np.inf], np.nan).fillna(1000)

df['NVI'] = pd.Series(nvi)

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Adj Close'])
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['NVI'], label='Negative Volume Index', color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Negative Volume Index')
ax2.set_xlabel('Date')
plt.show()

# ## Candlestick with Negative Volume Index
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
ax2.plot(df['NVI'], label='Negative Volume Index', color='red')
ax2.grid()
ax2.legend(loc='best')
ax2.set_ylabel('Negative Volume Index')
ax2.set_xlabel('Date')
plt.show()