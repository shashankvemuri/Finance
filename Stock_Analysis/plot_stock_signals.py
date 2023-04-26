import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Set the symbol and number of signals
symbol = 'AMD'
num_of_signals = 10

# Set the start and end dates for the data
start = dt.date.today() - dt.timedelta(days=394)
end = dt.date.today()

# Download the data using yfinance
df = yf.download(symbol, start, end)

# Get the list of closing prices and sort them in ascending order
closes = df.Close.tolist()
closes = sorted(closes)

# Calculate the low and high thresholds for the signals
low = closes[num_of_signals]
high = closes[-num_of_signals]

# Create a new column called 'Signal' and set all values to 0
df['Signal'] = 0

# Update the 'Signal' column based on the low and high thresholds
df.loc[df['Adj Close'] > high, 'Signal'] = -1
df.loc[df['Adj Close'] < low, 'Signal'] = 1

# Get the rows where the Signal column is 1 or -1
buys = df.loc[df['Signal'] == 1]
sells = df.loc[df['Signal'] == -1]

# Create a plot of the closing prices with markers for the buy and sell signals
plt.figure(figsize=(16, 8))
plt.plot(df.index, df['Adj Close'], label='Closing')
plt.plot(sells.index, df.loc[sells.index]['Adj Close'], 'v', markersize=10, color='r', label='Short')
plt.plot(buys.index, df.loc[buys.index]['Adj Close'], '^', markersize=10, color='g', label='Long')
plt.title(symbol + ' signals')
plt.ylabel('Price')
plt.xlabel('Date')
plt.legend(loc='best')
plt.show()