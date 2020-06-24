import pandas as pd
from pandas_datareader import DataReader
import datetime as dt
from stockstats import StockDataFrame
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ticker = 'AAPL'
num_of_years = 1
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.datetime.now() 

df = DataReader(ticker, 'yahoo', start, now)
df.columns = ['high', 'low', 'open', 'close', 'volume', 'adj close']
df = df[['open', 'close', 'high', 'low', 'volume']]
stock = StockDataFrame.retype(df)
print (stock['rsi_12'])

plt.gcf()
plt.plot(stock['boll'])
plt.plot(stock['boll_ub'])
plt.plot(stock['boll_lb'])