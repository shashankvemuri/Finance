import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
from pandas_datareader import DataReader

ticker = input('Enter a ticker: ')
start_date = dt.datetime.now() - dt.timedelta(days=int(365.25*10))
end_date = dt.date.today()

style.use('ggplot')
df = DataReader(ticker, 'yahoo', start_date, end_date)
df_ohlc = df['Adj Close'].resample('10D').ohlc()
df_ohlc.fillna(method="ffill",inplace=True)
df_ohlc.fillna(method="bfill",inplace=True)
df_volume = df['Volume'].resample('10D').sum()
df_volume.fillna(method="ffill",inplace=True)
df_volume.fillna(method="bfill",inplace=True)
df_ohlc.reset_index(inplace=True)
df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)
ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
ax1.xaxis_date()
candlestick_ohlc(ax1, df_ohlc.values, width=5, colorup='g')
ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
plt.show()