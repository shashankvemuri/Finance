import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D  
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms
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

# Line Chart
plt.figure(figsize=(14,7))
plt.plot(df['Adj Close'])
y_lim = plt.ylim()
x_lim = plt.xlim()
plt.plot(x_lim, y_lim, 'k-', color = 'r', label='45 degree')
plt.ylim(y_lim)
plt.xlim(x_lim)
plt.title('Stock of GANN Angles')
plt.legend(loc='best')
plt.show()

import math
angles = [82.5,75,71.25,63.75,45,26.25,18.75,15,7.5]
# radians = [0,7.5,15,18.5,26.25,45,63.75,71.25,75,82.5,90]
radians = [0.1309,0.261799,0.3228859,0.45814893,0.785398,1.1126474,1.2435471,1.309,1.439897]
# math.degrees(angles)
fig, ax = plt.subplots(figsize=(20,12))
ax.plot(df.index, df['Adj Close'])

x_0 = 0
y_0 = 0  


for i in range(len(radians)):
    ax.plot([df.index[0], df.index[-1]], [df['Adj Close'][0], math.degrees(math.radians(i)*(180/math.pi))], marker='^', markersize=10, label=angles[i])
    #ax.plot([df.index[0], df.index[-1]], [df['Adj Close'][0], math.degrees(i)], marker='^', markersize=10, label=angles[i])

plt.legend(title="Angles")
plt.show()


# ## Candlestick with GANN Lines Angles
from matplotlib import dates as mdates
df['VolumePositive'] = df['Open'] < df['Adj Close']
dfc = df.dropna()
dfc = df.reset_index()
dfc['Date'] = mdates.date2num(dfc['Date'].tolist())
from mplfinance.original_flavor import candlestick_ohlc
# Plot Example Angle line
angles = [82.5,75,71.25,63.75,45,26.25,18.75,15,7.5]

# plot the points
fig = plt.figure(figsize=(14,7))
ax = plt.subplot(111)

candlestick_ohlc(ax,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
x_0 = 0
y_0 = 0  

for i in range(len(angles)):
    ax.plot([df.index[0], df.index[-1]], [df['Adj Close'][0], math.degrees(math.radians(i)*(180/math.pi))], marker='^', markersize=10, label=angles[i])
    
axv = ax.twinx()
colors = df.VolumePositive.map({True: 'g', False: 'r'})
axv.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
axv.axes.yaxis.set_ticklabels([])
axv.set_ylim(0, 3*dfc.Volume.max())
ax.grid(True)
ax.set_title('Stock Closing Price')
ax.set_ylabel('Price')
ax.set_xlabel('Date')
ax.legend(loc='best')
plt.show()