import pandas as pd
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta
import talib
from pylab import rcParams 
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.pylab import date2num
from pandas_datareader import DataReader

ticker = "NIO"

#Get Dates
start_date = datetime.datetime.now() - datetime.timedelta(days=3650)
end_date = datetime.date.today()

def get_price_hist(ticker):    
    #Get data 
    data = DataReader(ticker, 'yahoo', start_date, end_date)
    return data


def get_indicators(data):
    # Get MACD
    data["macd"], data["macd_signal"], data["macd_hist"] = talib.MACD(data['Close'])
    
    # Get MA10 and MA30
    data["ma10"] = talib.MA(data["Close"], timeperiod=10)
    data["ma30"] = talib.MA(data["Close"], timeperiod=30)
    
    # Get RSI
    data["rsi"] = talib.RSI(data["Close"])
    return data


def plot_chart(data, n, ticker):
    
    # Filter number of observations to plot
    data = data.iloc[-n:]
    
    # Create figure and set axes for subplots
    fig = plt.figure()
    fig.suptitle('{} Technical Indicators'.format(ticker))
    rcParams['figure.figsize'] = 15, 10
    ax_candle = fig.add_axes((0, 0.72, 1, 0.20))
    ax_macd = fig.add_axes((0, 0.48, 1, 0.20), sharex=ax_candle)
    ax_rsi = fig.add_axes((0, 0.24, 1, 0.20), sharex=ax_candle)
    ax_vol = fig.add_axes((0, 0, 1, 0.20), sharex=ax_candle)
    
    # Format x-axis ticks as dates
    ax_candle.xaxis_date()
    
    # Get nested list of date, open, high, low and close prices
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
    ax_macd.plot(data.index, data["macd"], label="macd")
    ax_macd.bar(data.index, data["macd_hist"] * 3, label="hist")
    ax_macd.plot(data.index, data["macd_signal"], label="signal")
    ax_macd.legend()
    
    # Plot RSI
    # Above 70% = overbought, below 30% = oversold
    ax_rsi.set_ylabel("(%)")
    ax_rsi.plot(data.index, [70] * len(data.index), label="overbought")
    ax_rsi.plot(data.index, [30] * len(data.index), label="oversold")
    ax_rsi.plot(data.index, data["rsi"], label="rsi")
    ax_rsi.legend()
    
    # Show volume in millions
    ax_vol.bar(data.index, data["Volume"] / 1000000, label = "Volume")
    ax_vol.set_ylabel("(Million)")
    
    plt.show()
    

dataframe = get_price_hist(ticker)
#print(dataframe)

frame = get_indicators(dataframe)
print(frame.tail(60))

plot_chart(frame, 180, ticker)
