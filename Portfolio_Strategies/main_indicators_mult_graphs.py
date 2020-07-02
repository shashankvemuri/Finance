import matplotlib.pyplot as plt
from pylab import rcParams
import yfinance as yf
import datetime as dt
import warnings
import talib 
import ta

warnings.filterwarnings("ignore")
yf.pdr_override()

# input
symbol = 'TSLA'
num_of_years = 1
start = dt.date.today() - dt.timedelta(days = int(365.25 * num_of_years))
end = dt.date.today()

# Read data 
data = yf.download(symbol,start,end)

# ## SMA and EMA
#Simple Moving Average
data['SMA'] = talib.SMA(data['Adj Close'], timeperiod = 20)

# Exponential Moving Average
data['EMA'] = talib.EMA(data['Adj Close'], timeperiod = 20)

# Plot
rcParams['figure.figsize'] = 15,10
data[['Adj Close','SMA','EMA']].plot(figsize=(15, 10))
plt.xlabel('Dates')
plt.ylabel('Close Price')
plt.title(f'SMA vs. EMA for {symbol.upper()}')
plt.show()


# ## Bollinger Bands
# Bollinger Bands
data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['Adj Close'], timeperiod =20)

# Plot
data[['Adj Close','upper_band','middle_band','lower_band']].plot(figsize=(15,10))
plt.show()


# ## MACD (Moving Average Convergence Divergence)
# MACD
data['macd'], data['macdsignal'], data['macdhist'] = talib.MACD(data['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)
data[['macd','macdsignal']].plot(figsize=(15,10))
plt.xlabel('Dates')
plt.ylabel('MACD')
plt.title(f'Moving Average Convergence Divergence for {symbol.upper()}')
plt.show()


# ## RSI (Relative Strength Index)
# RSI
data['RSI'] = talib.RSI(data['Adj Close'], timeperiod=14)
# Plotting RSI
fig,ax = plt.subplots(figsize=(15, 10))
ax.plot(data.index, data.RSI, label='RSI')
ax.fill_between(data.index, y1=30, y2=70, color = 'lightcoral', alpha=0.3)
ax.set_xlabel('Date')
ax.set_ylabel('RSI')
ax.set_title(f'Relative Strength Index for {symbol.upper()}')
plt.show()


# ## OBV (On Balance Volume)
# OBV
data['OBV'] = talib.OBV(data['Adj Close'], data['Volume'])/10**6

fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle(f'Close Price vs. On Balance Volume for {symbol.upper()}')
ax1.plot(data['Adj Close'])
ax1.set_ylabel('Close')
ax2.plot(data['OBV'])
ax2.set_ylabel('On Balance Volume (in millions)')
plt.show()

## CCI (Commodity Channel Index)
# CCI
cci = ta.trend.cci(data['High'], data['Low'], data['Close'], n=31, c=0.015)
plt.subplots()
rcParams['figure.figsize'] = 15,10
plt.plot(cci)
plt.axhline(y=0, color='r', linestyle='-')
plt.xlabel('Dates')
plt.ylabel('Commodity Channel Index')
plt.title(f'Commodity Channel Index for {symbol.upper()}')
plt.show()