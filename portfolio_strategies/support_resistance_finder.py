import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
from pandas_datareader import data as pdr
import datetime

# Function to retrieve stock data
def fetch_stock_data(ticker, start_date, end_date):
    df = pdr.get_data_yahoo(ticker, start=start_date, end=end_date).reset_index()
    df["Date"] = df["Date"].apply(mpl_dates.date2num)
    return df[['Date', 'Open', 'High', 'Low', 'Close']]

# Function to identify support and resistance levels
def identify_levels(df):
    levels = []
    for i in range(2, df.shape[0] - 2):
        if is_support(df, i):
            levels.append((i, df["Low"][i], "Support"))
        elif is_resistance(df, i):
            levels.append((i, df["High"][i], "Resistance"))
    return levels

# Define support and resistance checks
def is_support(df, i):
    return df["Low"][i] < min(df["Low"][i - 1], df["Low"][i + 1])

def is_resistance(df, i):
    return df["High"][i] > max(df["High"][i - 1], df["High"][i + 1])

# Function to plot support and resistance levels
def plot_support_resistance(df, levels):
    fig, ax = plt.subplots()
    candlestick_ohlc(ax, df.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
    ax.xaxis.set_major_formatter(mpl_dates.DateFormatter('%d-%m-%Y'))

    for level in levels:
        plt.hlines(level[1], xmin=df["Date"][level[0]], xmax=max(df["Date"]), colors="blue")
    plt.title(f"Support and Resistance for {ticker.upper()}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()

# Main
ticker = input("Enter a ticker: ")
num_of_years = 0.2
start_date = datetime.date.today() - datetime.timedelta(days=int(365.25 * num_of_years))
end_date = datetime.date.today()

df = fetch_stock_data(ticker, start_date, end_date)
levels = identify_levels(df)
plot_support_resistance(df, levels)