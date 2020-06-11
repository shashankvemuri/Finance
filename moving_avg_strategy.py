import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'NIO'
start = dt.date.today() - dt.timedelta(days = 365*10)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)

df['SMA_20'] = df['Adj Close'].rolling(20).mean()
df['SMA_40'] = df['Adj Close'].rolling(40).mean()
df['SMA_80'] = df['Adj Close'].rolling(80).mean()

fig, ax = plt.subplots(figsize=(16,9))

ax.plot(df.index, df['Adj Close'], label='Price')
ax.plot(df.index, df['SMA_20'], label = '20-days SMA')
ax.plot(df.index, df['SMA_40'], label = '40-days SMA')
ax.plot(df.index, df['SMA_80'], label = '80-days SMA')

ax.legend(loc='best')
ax.set_ylabel('Price')
ax.set_title('Big Three Trading Strategy')

new_dates = df['2019-01-01':'2020-06-05']
print(new_dates.head())

plt.figure(figsize=(16,10))
plt.plot(new_dates['Adj Close'], label='Price')
plt.plot(new_dates['SMA_20'], label = '20-days SMA')
plt.plot(new_dates['SMA_40'], label = '40-days SMA')
plt.plot(new_dates['SMA_80'], label = '80-days SMA')
plt.legend(loc='best')
plt.grid(True)
plt.ylabel('Price')
plt.xlabel('Dates')
plt.title('Big Three Trading Strategy')

plt.figure(figsize=(16,10))
plt.plot_date(x=new_dates.index ,y=new_dates['Adj Close'], label='Price')
plt.plot(new_dates['SMA_20'], label = '20-days SMA')
plt.plot(new_dates['SMA_40'], label = '40-days SMA')
plt.plot(new_dates['SMA_80'], label = '80-days SMA')
plt.legend(loc='best')
plt.grid(True)
plt.ylabel('Price')
plt.xlabel('Dates')
plt.title('Big Three Trading Strategy')

plt.figure(figsize=(16,10))
plt.plot_date(x=new_dates.index ,y=new_dates['Adj Close'], fmt='r-', label='Price')
plt.plot(new_dates['SMA_20'], label = '20-days SMA', color='b')
plt.plot(new_dates['SMA_40'], label = '40-days SMA', color='y')
plt.plot(new_dates['SMA_80'], label = '80-days SMA', color='green')
plt.legend(loc='best')
plt.grid(True)
plt.ylabel('Price')
plt.xlabel('Date')
plt.title('Big Three Trading Strategy')
plt.show()