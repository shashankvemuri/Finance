# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas_datareader import DataReader

# Get the ticker symbol from the user
ticker = input("Enter a ticker: ")
ticker = str(ticker)

# Set the start and end dates for stock data retrieval
num_of_years = 6
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now()

# Retrieve the stock data for the given ticker and date range
stock = DataReader(ticker, 'yahoo', start_date, end_date)

# Calculate the Simple Moving Averages with 50-day and 200-day windows
SMA50 = pd.DataFrame()
SMA50['Close Price'] = stock['Close'].rolling(window=50).mean()

SMA200 = pd.DataFrame()
SMA200['Close Price'] = stock['Close'].rolling(window=200).mean()

# Combine the stock data and SMA data into a single dataframe
data = pd.DataFrame()
data['stock'] = stock['Close']
data['SMA 50'] = SMA50['Close Price']
data['SMA 200'] = SMA200['Close Price']

def buy_sell(data):
    # Initialize the signal price arrays and flag
    sigPriceBuy=[]
    sigPriceSell=[]
    flag=-1

    # Iterate through the data to generate buy and sell signals
    for i in range(len(data)):
        # Buy signal when SMA 50 is greater than SMA 200 and previous signal was not buy
        if data['SMA 50'][i]>data['SMA 200'][i]:
            if flag != 1:
                sigPriceBuy.append(data['stock'][i])
                sigPriceSell.append(np.nan)
                flag=1
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        # Sell signal when SMA 50 is less than SMA 200 and previous signal was not sell
        elif data['SMA 50'][i]<data['SMA 200'][i]:
            if flag != 0 :
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(data['stock'][i])
                flag = 0
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        # No signal when SMA 50 is equal to SMA 200
        else:
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)

    # Return the signal price arrays
    return(sigPriceBuy,sigPriceSell)

# Generate the buy and sell signal arrays
buy_sell = buy_sell(data)

# Add the buy and sell signal arrays to the data dataframe
data['Buy_Signal_Price'] = buy_sell[0]
data['Sell_Signal_Price'] = buy_sell[1]

# Plot the stock data with the SMA data and buy/sell signals
plt.figure(figsize=(15,10))
plt.plot(stock['Close'],label = f'{ticker.upper()} Close Price',alpha=0.35)
plt.plot(SMA50['Close Price'],label = 'SMA 50' ,alpha=0.35)
plt.plot(SMA200['Close Price'],label = 'SMA 200' ,alpha=0.35)
plt.scatter(data.index,data['Buy_Signal_Price'],label='Buy',marker='^',color='green')
plt.scatter(data.index,data['Sell_Signal_Price'],label='Sell',marker='v',color='red')
plt.title(f'{ticker.upper()} Close Price History Buy and Sell Signals')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend(loc='upper left')
plt.show()