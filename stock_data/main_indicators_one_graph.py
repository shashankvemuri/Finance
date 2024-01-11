import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.ticker as mticker
import datetime as dt
from pylab import rcParams

# Override pandas_datareader's default method to use Yahoo Finance
yf.pdr_override()

# Define the moving averages to be used
smas_used = [10, 30, 50]

# Calculate the start date for historical data retrieval
start = pd.Timestamp("2020-01-01") - pd.Timedelta(days=max(smas_used))
now = pd.Timestamp.now()

# Ask the user for a stock symbol
stock = input("Enter the stock symbol: ")

while stock != "quit":
    # Retrieve stock data from Yahoo Finance
    prices = pdr.get_data_yahoo(stock, start, now)

    # Calculate moving averages and Bollinger Bands
    for sma in smas_used:
        prices[f"SMA_{sma}"] = prices["Close"].rolling(window=sma).mean()
    
    # Bollinger Bands
    bb_period = 15
    stdev = 2
    prices[f"SMA{bb_period}"] = prices["Close"].rolling(window=bb_period).mean()
    prices["STDEV"] = prices["Close"].rolling(window=bb_period).std()
    prices["LowerBand"] = prices[f"SMA{bb_period}"] - (stdev * prices["STDEV"])
    prices["UpperBand"] = prices[f"SMA{bb_period}"] + (stdev * prices["STDEV"])
    prices["Date"] = mdates.date2num(prices.index)

    # Calculate 10.4.4 Stochastic indicator
    period = 10
    k = 4
    d = 4
    prices["RolHigh"] = prices["High"].rolling(window=period).max()
    prices["RolLow"] = prices["Low"].rolling(window=period).min()
    prices["stok"] = ((prices["Close"] - prices["RolLow"]) / (prices["RolHigh"] - prices["RolLow"])) * 100
    prices["K"] = prices["stok"].rolling(window=k).mean()
    prices["D"] = prices["K"].rolling(window=d).mean()

    # Prepare data for plotting
    ohlc = []
    prices = prices.iloc[max(smas_used):]
    for i, (date, row) in enumerate(prices.iterrows()):
        append_me = (prices["Date"][i], prices["Open"][i], prices["High"][i], prices["Low"][i], prices["Close"][i], prices["Volume"][i])
        ohlc.append(append_me)

    # Create and plot the figure with the calculated indicators
    fig, ax1 = plt.subplots()
    candlestick_ohlc(ax1, ohlc, width=0.5, colorup="k", colordown="r", alpha=0.75)
    
    # Plot moving averages and Bollinger Bands
    for x in smas_used:
        prices[f"SMA_{x}"].plot(label="close")
    prices["UpperBand"].plot(label="close", color="lightgray")
    prices["LowerBand"].plot(label="close", color="lightgray")

    # Set up the plot
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(8))
    plt.tick_params(axis="x", rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(f"{stock.upper()} - Daily")
    plt.ylim(prices["Low"].min(), prices["High"].max() * 1.05)
    rcParams["figure.figsize"] = 20, 10

    # Show the plot
    plt.show()

    # Ask for another stock symbol
    stock = input("Enter the stock symbol: ")