import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import talib as ta
import datetime as dt

# input
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days = 365*10)
end = dt.date.today()

# Read data 
data = yf.download(symbol,start,end)

# ## SMA and EMA
#Simple Moving Average
data['SMA'] = ta.SMA(data['Adj Close'], timeperiod = 20)

# Exponential Moving Average
data['EMA'] = ta.EMA(data['Adj Close'], timeperiod = 20)

# Plot
data[['Adj Close','SMA','EMA']].plot(figsize=(10,5))
plt.subplots()
plt.show()


# ## Bollinger Bands
# Bollinger Bands
data['upper_band'], data['middle_band'], data['lower_band'] = ta.BBANDS(data['Adj Close'], timeperiod =20)

# Plot
data[['Adj Close','upper_band','middle_band','lower_band']].plot(figsize=(10,5))
plt.show()


# ## MACD (Moving Average Convergence Divergence)
# MACD
data['macd'], data['macdsignal'], data['macdhist'] = ta.MACD(data['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)
data[['macd','macdsignal']].plot(figsize=(10,5))

plt.show()


# ## RSI (Relative Strength Index)
# RSI
data['RSI'] = ta.RSI(data['Adj Close'], timeperiod=14)
# Plotting RSI
fig,ax = plt.subplots(figsize=(10,5))
ax.plot(data.index, data.RSI, label='RSI')
ax.fill_between(data.index, y1=30, y2=70, color = 'lightcoral', alpha=0.3)
ax.set_xlabel('Date')
ax.set_ylabel('RSI')
plt.show()


# ## OBV (On Balance Volume)
# OBV
data['OBV'] = ta.OBV(data['Adj Close'], data['Volume'])/10**6

data['Adj Close'].plot()
plt.ylabel('Close')
plt.show()

data.OBV.plot()
plt.ylabel('On Balance Volume (in millions)')
plt.show()