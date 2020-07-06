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
symbol = str(input('Enter a ticker: '))
symbol = symbol.strip()
symbol = symbol.upper()

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

# Bollinger Bands
data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['Adj Close'], timeperiod =20)

# Plot
rcParams['figure.figsize'] = 15,10
fig, (ax1, ax2) = plt.subplots(2)
ax1.plot(data[['Adj Close','SMA','EMA']])
ax1.legend(('Adj Close', 'SMA', 'EMA'))
ax1.set_ylabel('Close Price')
ax1.set_title(f'SMA vs. EMA for {symbol.upper()}')

ax2.plot(data[['Adj Close','upper_band','middle_band','lower_band']])
ax2.legend(('Adj Close', 'Upper Band', 'Middle Band', 'Lower Band'))
ax2.set_xlabel('Dates')
ax2.set_ylabel('Adj Close Price')
ax2.set_title(f'Bollinger Bands for {symbol.upper()}')
ax2.fill_between(data.index, y1=data['lower_band'], y2=data['upper_band'], color = 'lightcoral', alpha=0.3)
plt.show()


# ## MACD (Moving Average Convergence Divergence)
# MACD
data['macd'], data['macdsignal'], data['macdhist'] = talib.MACD(data['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)

# Plot
rcParams['figure.figsize'] = 15,10
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle(f'Close Price vs. Commodity Channel Index for {symbol.upper()}')
ax1.plot(data['Adj Close'])
ax1.set_ylabel('Adj Close')

ax2.plot(data[['macd','macdsignal']])
ax2.legend(('MACD', 'MACD Signal'))
ax2.set_ylabel('MACD')
ax2.set_title(f'Moving Average Convergence Divergence for {symbol.upper()}')

## CCI (Commodity Channel Index)
# CCI
cci = ta.trend.cci(data['High'], data['Low'], data['Close'], n=31, c=0.015)

rcParams['figure.figsize'] = 15,10
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle(f'Close Price vs. Commodity Channel Index for {symbol.upper()}')
ax1.plot(data['Adj Close'])
ax1.set_ylabel('Adj Close')

ax2.plot(cci)
ax2.axhline(y=0, color='r', linestyle='-')
ax2.set_xlabel('Dates')
ax2.set_ylabel('Commodity Channel Index')
ax2.set_title(f'Commodity Channel Index for {symbol.upper()}')
plt.show()


# ## RSI (Relative Strength Index)
# RSI
data['RSI'] = talib.RSI(data['Adj Close'], timeperiod=14)
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle(f'Close Price vs. Relative Strength Index for {symbol.upper()}')
ax1.plot(data['Adj Close'])
ax1.set_ylabel('Adj Close')

ax2.plot(data['RSI'])
ax2.fill_between(data.index, y1=30, y2=70, color = 'lightcoral', alpha=0.3)
ax2.set_ylabel('RSI')
plt.show()

# ## OBV (On Balance Volume)
# OBV
data['OBV'] = talib.OBV(data['Adj Close'], data['Volume'])/10**6

fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle(f'Close Price vs. On Balance Volume for {symbol.upper()}')
ax1.plot(data['Adj Close'])
ax1.set_ylabel('Adj Close')

ax2.plot(data['OBV'])
ax2.set_ylabel('On Balance Volume (in millions)')
plt.show()