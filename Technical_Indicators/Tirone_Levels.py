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
df['Adj Close'][-1]

print('Lowest Price:', df['Adj Close'].min())
print('Highest Price:', df['Adj Close'].max())
print('Mean Price:', df['Adj Close'].mean())
print('Lowest Low:', df['Low'].min())
print('Highest High:', df['High'].max())

# ## Midpoint Method
Top_Line = abs(((df['High'].max() - df['Low'].min())/3) - df['High'].max())
Center_Line = ((df['High'].max() - df['Low'].min())/2) + df['Low'].min()
Bottom_Line = ((df['High'].max() - df['Low'].min())/3) + df['Low'].min()

# ## Mean Method
Adjusted_Mean = abs((df['High'].max() + df['Low'].min() + df['Adj Close'][-1])/3)
#Adjusted_Mean = (df['High'].max() + df['Low'].min() + df['Adj Close'].mean())/3
Extreme_High = abs((df['High'].max()  - df['Low'].min()) + Adjusted_Mean)
Regular_High = abs((Adjusted_Mean*2) - df['Low'].min())
Regular_Low = abs((Adjusted_Mean*2) - df['High'].max())
Extreme_Low = abs((df['High'].max() - df['Low'].min()) - Adjusted_Mean)

# ## Line Chart
# Line Chart
plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
plt.axhline(Top_Line, color='green', label='Top Line')
plt.axhline(Center_Line, color='orange', linestyle='--',label='Center Line')
plt.axhline(Bottom_Line, color='red', label='Bottom Line')
plt.legend(loc='best')
plt.title('Stock of Midpoint Method')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# Line Chart
plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
plt.axhline(Extreme_High, color='darkgreen', label='Extreme High')
plt.axhline(Regular_High, color='green', label='Regular High')
plt.axhline(Adjusted_Mean, color='darkblue', linestyle='--',label='Adjusted Mean')
plt.axhline(Regular_Low, color='orange', label='Regular Low')
plt.axhline(Extreme_Low, color='red', label='Extreme Low')
plt.legend(loc='best')
plt.title('Stock of Mean Method')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# ## Candlestick
from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())

from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.axhline(Top_Line, color='green', label='Top Line')
ax1.axhline(Center_Line, color='orange', linestyle='--',label='Center Line')
ax1.axhline(Bottom_Line, color='red', label='Bottom Line')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price (Midpoint Method)')
ax1.set_ylabel('Price')
ax1.legend()
plt.show()

from mplfinance.original_flavor import candlestick_ohlc
fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(111)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.axhline(Extreme_High, color='darkgreen', label='Extreme High')
ax1.axhline(Regular_High, color='green', label='Regular High')
ax1.axhline(Adjusted_Mean, color='darkblue', linestyle='--',label='Adjusted Mean')
ax1.axhline(Regular_Low, color='orange', label='Regular Low')
ax1.axhline(Extreme_Low, color='red', label='Extreme Low')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price (Mean Method)')
ax1.set_ylabel('Price')
ax1.legend()
plt.show()