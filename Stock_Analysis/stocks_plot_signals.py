import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

symbol = 'AMD'
num_of_signals = 10

start = dt.date.today() - dt.timedelta(days=394)
end = dt.date.today()

df = yf.download(symbol,start,end)

closes = df.Close.tolist()
closes = sorted(closes)
low = closes[num_of_signals]
high = closes[-num_of_signals]

df['Signal'] = 0

df.loc[df['Adj Close'] > high, 'Signal'] = -1
df.loc[df['Adj Close'] < low, 'Signal'] = 1

buys = df.loc[df['Signal'] == 1]
sells = df.loc[df['Signal'] == -1]

plt.figure(figsize=(16,8))
plt.plot(df.index, df['Adj Close'], label='Closing')
plt.plot(sells.index, df.loc[sells.index]['Adj Close'],'v', markersize=10, color='r', label='Short')
plt.plot(buys.index, df.loc[buys.index]['Adj Close'], '^', markersize=10, color='g', label='Long')
plt.title(symbol + ' signals')
plt.ylabel('Price')
plt.xlabel('Date')
plt.legend(loc='best')
plt.show()