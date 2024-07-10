import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
from pandas_datareader import data as pdr
yf.pdr_override()

# Setting parameters
num_of_years = 40
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.date(2020, 10, 3)

# Get user input for stock ticker
stock = input("Enter the stock symbol: ")

# Loop until user enters 'quit'
while stock.lower() != "quit":
    # Fetch stock data
    df = pdr.get_data_yahoo(stock, start, now)

    # Calculate Simple Moving Average (SMA)
    sma = 50
    df['SMA' + str(sma)] = df['Adj Close'].rolling(window=sma).mean()
    
    # Calculate percentage change from SMA
    df['PC'] = ((df["Adj Close"] / df['SMA' + str(sma)]) - 1) * 100

    # Calculating statistics
    mean = df["PC"].mean()
    stdev = df["PC"].std()
    current = df["PC"].iloc[-1]
    yday = df["PC"].iloc[-2]

    # Displaying statistics
    print(f"Mean: {mean:.2f}, Standard Deviation: {stdev:.2f}, Current: {current:.2f}, Yesterday: {yday:.2f}")

    # Histogram settings
    bins = np.arange(-100, 100, 1)
    plt.figure(figsize=(15, 10))
    plt.hist(df["PC"], bins=bins, alpha=0.5)
    plt.title(f"{stock} - % From {sma} SMA Histogram since {start.year}")
    plt.xlabel(f'Percent from {sma} SMA (bin size = 1)')
    plt.ylabel('Count')

    # Adding vertical lines for mean, std deviation, current and yesterday's percentage change
    for i in range(-3, 4):
        plt.axvline(x=mean + i * stdev, color='gray', linestyle='--', alpha=0.5 + abs(i)/6)
    plt.axvline(x=current, color='red', label='Today')
    plt.axvline(x=yday, color='blue', label='Yesterday')
    plt.legend()
    plt.show()

    # Next user input
    stock = input("Enter the stock symbol: ")