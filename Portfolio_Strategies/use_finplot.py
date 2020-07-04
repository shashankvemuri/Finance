import finplot as fplt
import numpy as np
import pandas as pd
import requests
import pyqtgraph
import yfinance as yf
import datetime as dt

# define time range 
start = dt.date.today() - dt.timedelta(days = 365*10)
end = dt.datetime.now()
stock = 'AAPL'

df = yf.download(stock,start, end, interval='1d')

# format it in pandas
df = df.reset_index()
df = df.drop(columns = ['Adj Close'])
df = df.rename(columns={'Date':'time', 'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'})
df = df.astype({'time':'datetime64[ns]'})

# create two plots
ax,ax2 = fplt.create_plot(stock, rows=2)

# plot candle sticks
candles = df[['time','open','close','high','low']]
fplt.candlestick_ochl(candles, ax=ax)

# overlay volume on the top plot
volumes = df[['time','open','close','volume']]
fplt.volume_ocv(volumes, ax=ax.overlay())

# put an MA on the close price
fplt.plot(df['time'], df['close'].rolling(25).mean(), ax=ax, legend='ma-25')

# place some markers on low wicks
lo_wicks = df[['open','close']].T.min() - df['low']
df.loc[(lo_wicks>lo_wicks.quantile(0.99)), 'marker'] = df['low']
fplt.plot(df['time'], df['marker'], ax=ax, color='#4a5', style='^')

# draw something random on our second plot
fplt.plot(df['time'], np.random.normal(size=len(df)), ax=ax2, color='#927', legend='random')
fplt.set_y_range(-1.4, +3.7, ax=ax2) # hard-code y-axis range limitation

# we're done
fplt.show()