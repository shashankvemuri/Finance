# Import relevant libraries
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.ticker as mticker
import datetime as dt
from pylab import rcParams

# Set yfinance to use pandas datareader
yf.pdr_override()

# Choose smas
smas_used = [10, 30, 50]

start = pd.Timestamp("2020-01-01") - pd.Timedelta(days=max(smas_used))
now = pd.Timestamp.now()

# Get stock symbol from user
stock = input("Enter the stock symbol: ")

while stock != "quit":

    # Get stock data
    prices = pdr.get_data_yahoo(stock, start, now)

    # Create figure and axis objects
    fig, ax1 = plt.subplots()

    # Calculate moving averages
    for sma in smas_used:
        prices[f"SMA_{sma}"] = prices["Close"].rolling(window=sma).mean()

    # Calculate Bollinger Bands
    bb_period = 15
    stdev = 2
    prices[f"SMA{bb_period}"] = prices["Close"].rolling(window=bb_period).mean()
    prices["STDEV"] = prices["Close"].rolling(window=bb_period).std()
    prices["LowerBand"] = prices[f"SMA{bb_period}"] - (stdev * prices["STDEV"])
    prices["UpperBand"] = prices[f"SMA{bb_period}"] + (stdev * prices["STDEV"])
    prices["Date"] = mdates.date2num(prices.index)

    # Calculate 10.4.4 stochastic
    period = 10
    k = 4
    d = 4

    prices["RolHigh"] = prices["High"].rolling(window=period).max()
    prices["RolLow"] = prices["Low"].rolling(window=period).min()
    prices["stok"] = ((prices["Close"] - prices["RolLow"]) / (prices["RolHigh"] - prices["RolLow"])) * 100
    prices["K"] = prices["stok"].rolling(window=k).mean()
    prices["D"] = prices["K"].rolling(window=d).mean()

    # Prepare for plotting GD (green dots)
    prices["GD"] = prices["High"]
    ohlc = []
    prices = prices.iloc[max(smas_used):]

    # Prepare for plotting BBLB (blue dots)
    green_dot_date = []
    green_dot = []
    last_k = 0
    last_d = 0
    last_low = 0
    last_close = 0
    last_low_bb = 0

    # Iterate over prices to create candlesticks and GD+Blue dots
    for i, (date, row) in enumerate(prices.iterrows()):

        append_me = (prices["Date"][i], prices["Open"][i], prices["High"][i], prices["Low"][i],
                     prices["Close"][i], prices["Volume"][i])
        ohlc.append(append_me)

        # Check for Green Dot
        if prices["K"][i] > prices["D"][i] and last_k < last_d and last_k < 60:
            plt.plot(prices["Date"][i], prices["High"][i] + 1, marker="o", ms=4, ls="", color="g")
            green_dot_date.append(date)  # Store green dot date
            green_dot.append(prices["High"][i])  # Store green dot value

        # Check for Lower Bollinger Band Bounce
        if (
            ((last_low < last_low_bb) or (prices["Low"][i] < prices["LowerBand"][i]))
            and (
                prices["Adj Close"][i] > last_close
                and prices["Adj Close"][i] > prices["LowerBand"][i]
            )
            and last_k < 60
        ):
            plt.plot(
                prices["Date"][i],
                prices["Low"][i] - 1,
                marker="o",
                ms=4,
                ls="",
                color="b",
            )

        # Store values
        last_k = prices["K"][i]
        last_d = prices["D"][i]
        last_low = prices["Low"][i]
        last_close = prices["Adj Close"][i]
        last_low_bb = prices["LowerBand"][i]

    # Plot moving averages and BBands
    for x in smas_used:
        sma = x
        prices["SMA_" + str(sma)].plot(label="close")
    prices["UpperBand"].plot(label="close", color="lightgray")
    prices["LowerBand"].plot(label="close", color="lightgray")

    # Plot candlesticks
    candlestick_ohlc(ax1, ohlc, width=0.5, colorup="k", colordown="r", alpha=0.75)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(8))
    plt.tick_params(axis="x", rotation=45)

    # Pivot Points
    pivots = []
    dates = []
    counter = 0
    lastPivot = 0

    Range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dateRange = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in prices.index:
        currentMax = max(Range, default=0)
        value = round(prices["High"][i], 2)

        Range = Range[1:9]
        Range.append(value)
        dateRange = dateRange[1:9]
        dateRange.append(i)

        if currentMax == max(Range, default=0):
            counter += 1
        else:
            counter = 0
        if counter == 5:
            lastPivot = currentMax
            dateloc = Range.index(lastPivot)
            lastDate = dateRange[dateloc]
            pivots.append(currentMax)
            dates.append(lastDate)
    print()

    timeD = dt.timedelta(days=30)

    for index in range(len(pivots)):
        plt.plot_date(
            [dates[index] - (timeD * 0.075), dates[index] + timeD],
            [6 + pivots[index], pivots[index]],
            linestyle="--",
            linewidth=1,
            marker=",",
        )
        plt.annotate(
            str(pivots[index]),
            (mdates.date2num(dates[index]), pivots[index]),
            xytext=(-10, 7),
            textcoords="offset points",
            fontsize=7,
            arrowprops=dict(arrowstyle="-|>"),
        )

    # Customize
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(stock + " - Daily")
    plt.ylim(prices["Low"].min(), prices["High"].max() * 1.05)
    # plt.yscale("log")
    rcParams["figure.figsize"] = 20, 10
    plt.show()

    # Asks for new stock
    stock = input("Enter the stock symbol : ")