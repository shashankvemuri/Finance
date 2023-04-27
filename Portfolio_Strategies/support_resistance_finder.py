import pandas as pd
import numpy as np
import yfinance as yf
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import datetime

# Setup
yf.pdr_override()
plt.rcParams["figure.figsize"] = [15, 10]
plt.rc("font", size=14)

# Define the input parameters
ticker = input("Enter a ticker: ")
num_of_years = 0.2

# Define start and end dates
start_date = datetime.date.today() - datetime.timedelta(days=int(365.25 * num_of_years))
end_date = datetime.date.today()

# Retrieve the data from Yahoo Finance and create a pandas dataframe
df = pdr.get_data_yahoo(ticker, start_date, end_date).reset_index()

# Convert dates to matplotlib format
df["Date"] = df["Date"].apply(mpl_dates.date2num)

# Select the relevant columns
df = df.loc[:, ["Date", "Open", "High", "Low", "Close"]]

# Calculate support and resistance levels
def isSupport(df, i):
    support = (
        df["Low"][i] < df["Low"][i - 1]
        and df["Low"][i] < df["Low"][i + 1]
        and df["Low"][i + 1] < df["Low"][i + 2]
        and df["Low"][i - 1] < df["Low"][i - 2]
    )
    return support


def isResistance(df, i):
    resistance = (
        df["High"][i] > df["High"][i - 1]
        and df["High"][i] > df["High"][i + 1]
        and df["High"][i + 1] > df["High"][i + 2]
        and df["High"][i - 1] > df["High"][i - 2]
    )
    return resistance


levels = []
for i in range(2, df.shape[0] - 2):
    if isSupport(df, i):
        levels.append((i, df["Low"][i]))
    elif isResistance(df, i):
        levels.append((i, df["High"][i]))

# Plot support and resistance levels
def plot_all(df, levels):
    fig, ax = plt.subplots()
    plt.title(f"Support and Resistance for {ticker.upper()}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    candlestick_ohlc(
        ax, df.values, width=0.6, colorup="green", colordown="red", alpha=0.8
    )

    date_format = mpl_dates.DateFormatter("%d %b %Y")
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    fig.tight_layout()

    for level in levels:
        plt.hlines(
            level[1], xmin=df["Date"][level[0]], xmax=max(df["Date"]), colors="blue"
        )
    fig.show()

# Calculate the mean of the range of the stock price
s = np.mean(df["High"] - df["Low"])

# Take out close support and resistance levels
def isFarFromLevel(l, levels, s):
    return np.sum([abs(l - x) < s for x in levels]) == 0

# Add to list of levels
levels = []
for i in range(2, df.shape[0] - 2):
    if isSupport(df, i):
        l = df["Low"][i]
        w = "Support"
        if isFarFromLevel(l, levels, s):
            levels.append((i, l))
    elif isResistance(df, i):
        l = df["High"][i]
        w = "Resistance"

        if isFarFromLevel(l):
            levels.append((i, l))

# Identify dates and prices for each level
dates = [x[0] for x in levels]
prices = [x[1] for x in levels]

# Identify support or resistance on each date
which = []
for date, price in zip(dates, prices):
    for i in range(2, df.shape[0] - 2):
        if price == df["Low"][i]:
            w = "Support"

        elif price == df["High"][i]:
            w = "Resistance"

        else:
            continue
    which.append(w)

# Create and display dataframe with data
new_dates = [start_date + datetime.timedelta(days=date) for date in dates]
frame = pd.DataFrame(zip(new_dates, which, prices), columns=["Date", "Support or Resistance", "Price"]).set_index("Date")
print(frame)

# Plot data
plot_all()