# Import dependencies
import pandas as pd
import datetime
import talib
from dateutil.relativedelta import relativedelta
from pandas_datareader import DataReader
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.pylab import date2num
import matplotlib.pyplot as plt
from pylab import rcParams 

# Set ticker and date range
ticker = "NIO"
start_date = datetime.datetime.now() - datetime.timedelta(days=3650)
end_date = datetime.date.today()

def get_price_hist(ticker):    
    # Get stock data using pandas_datareader
    data = DataReader(ticker, 'yahoo', start_date, end_date)
    return data

def get_indicators(data):
    # Add technical indicators using talib
    data["macd"], data["macd_signal"], data["macd_hist"] = talib.MACD(data['Close'])
    data["ma10"] = talib.MA(data["Close"], timeperiod=10)
    data["ma30"] = talib.MA(data["Close"], timeperiod=30)
    data["rsi"] = talib.RSI(data["Close"])
    return data

def plot_chart(data, n, ticker):
    # Filter data to show only the last n observations
    data = data.iloc[-n:]
    
    # Create a new figure with subplots for each indicator
    fig = plt.figure()
    fig.suptitle('{} Technical Indicators'.format(ticker))
    rcParams['figure.figsize'] = 15, 10
    ax_candle = fig.add_axes((0, 0.72, 1, 0.20))
    ax_macd = fig.add_axes((0, 0.48, 1, 0.20), sharex=ax_candle)
    ax_rsi = fig.add_axes((0, 0.24, 1, 0.20), sharex=ax_candle)
    ax_vol = fig.add_axes((0, 0, 1, 0.20), sharex=ax_candle)
    
    # Format x-axis ticks as dates
    ax_candle.xaxis_date()
    
    # Convert data to a nested list for use with candlestick_ohlc
    ohlc = []
    for date, row in data.iterrows():
        openp, highp, lowp, closep = row[:4]
        ohlc.append([date2num(date), openp, highp, lowp, closep])
 
    # Plot candlestick chart
    ax_candle.plot(data.index, data["ma10"], label="MA10")
    ax_candle.plot(data.index, data["ma30"], label="MA30")
    candlestick_ohlc(ax_candle, ohlc, colorup="g", colordown="r", width=0.8)
    ax_candle.legend()
    
    # Plot MACD
    ax_macd.plot(data.index, data["macd"], label="MACD")
    ax_macd.bar(data.index, data["macd_hist"] * 3, label="Histogram")
    ax_macd.plot(data.index, data["macd_signal"], label="Signal")
    ax_macd.legend()
    
    # Plot RSI
    ax_rsi.set_ylabel("(%)")
    ax_rsi.plot(data.index, [70] * len(data.index), label="Overbought")
    ax_rsi.plot(data.index, [30] * len(data.index), label="Oversold")
    ax_rsi.plot(data.index, data["rsi"], label="rsi")
    ax_rsi.legend()
    
    # Plot volume (in millions)
    ax_vol.bar(data.index, data["Volume"] / 1000000, label = "Volume")
    ax_vol.set_ylabel("(Million)")
    
    plt.show()

# Display table and plot of indicator data 
dataframe = get_price_hist(ticker)
frame = get_indicators(dataframe)
print(frame.tail(60))
plot_chart(frame, 180, ticker)
