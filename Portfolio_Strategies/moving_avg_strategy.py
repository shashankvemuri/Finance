# Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Set the date range for data retrieval
start_date = dt.date.today() - dt.timedelta(days=365*10) # 10 years ago
end_date = dt.date.today()

# Set the stock symbol for data retrieval
symbol = 'NIO'

# Download the stock price data using Yahoo Finance API
yf.pdr_override() # override pandas-datareader method with yfinance method
df = yf.download(symbol, start_date, end_date)

# Calculate the moving averages
df['SMA_20'] = df['Adj Close'].rolling(20).mean() # 20-day Simple Moving Average
df['SMA_40'] = df['Adj Close'].rolling(40).mean() # 40-day Simple Moving Average
df['SMA_80'] = df['Adj Close'].rolling(80).mean() # 80-day Simple Moving Average

# Create the plot
fig, ax = plt.subplots(figsize=(16,9))

ax.plot(df.index, df['Adj Close'], label='Price') # plot the stock price
ax.plot(df.index, df['SMA_20'], label='20-days SMA') # plot the 20-day SMA
ax.plot(df.index, df['SMA_40'], label='40-days SMA') # plot the 40-day SMA
ax.plot(df.index, df['SMA_80'], label='80-days SMA') # plot the 80-day SMA

ax.legend(loc='best')
ax.set_ylabel('Price')
ax.set_title('Big Three Trading Strategy')

# Plot the selected date range
new_dates = df['2019-01-01':'2020-06-05']
print(new_dates.head())

plt.figure(figsize=(16,10))
plt.plot(new_dates['Adj Close'], label='Price')
plt.plot(new_dates['SMA_20'], label='20-days SMA')
plt.plot(new_dates['SMA_40'], label='40-days SMA')
plt.plot(new_dates['SMA_80'], label='80-days SMA')
plt.legend(loc='best')
plt.grid(True)
plt.ylabel('Price')
plt.xlabel('Dates')
plt.title('Big Three Trading Strategy')

# Plot the selected date range with dates as x-axis
plt.figure(figsize=(16,10))
plt.plot_date(x=new_dates.index, y=new_dates['Adj Close'], fmt='r-', label='Price')
plt.plot(new_dates['SMA_20'], label='20-days SMA', color='b')
plt.plot(new_dates['SMA_40'], label='40-days SMA', color='y')
plt.plot(new_dates['SMA_80'], label='80-days SMA', color='green')
plt.legend(loc='best')
plt.grid(True)
plt.ylabel('Price')
plt.xlabel('Date')
plt.title('Big Three Trading Strategy')
plt.show()