import pandas as pd
from pandas_datareader import DataReader
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# Function to retrieve stock data
def get_stock_data(ticker, start_date, end_date):
    return DataReader(ticker, 'yahoo', start_date, end_date)

# Function to calculate Simple Moving Averages (SMA)
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

# Function to generate buy and sell signals
def generate_signals(data):
    signal_buy = []
    signal_sell = []
    flag = -1

    for i in range(len(data)):
        if data['SMA 50'][i] > data['SMA 200'][i] and flag != 1:
            signal_buy.append(data['stock'][i])
            signal_sell.append(np.nan)
            flag = 1
        elif data['SMA 50'][i] < data['SMA 200'][i] and flag != 0:
            signal_buy.append(np.nan)
            signal_sell.append(data['stock'][i])
            flag = 0
        else:
            signal_buy.append(np.nan)
            signal_sell.append(np.nan)

    return signal_buy, signal_sell

# Main function to run the analysis
def main():
    ticker = input("Enter a ticker: ")
    num_of_years = 6
    start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
    end_date = dt.datetime.now()

    # Retrieve and process stock data
    stock_data = get_stock_data(ticker, start_date, end_date)
    stock_data['SMA 50'] = calculate_sma(stock_data, 50)
    stock_data['SMA 200'] = calculate_sma(stock_data, 200)

    # Generate buy and sell signals
    buy_signals, sell_signals = generate_signals(stock_data)

    # Plotting
    plt.figure(figsize=(15,10))
    plt.plot(stock_data['Close'], label='Close Price', alpha=0.35)
    plt.plot(stock_data['SMA 50'], label='SMA 50', alpha=0.35)
    plt.plot(stock_data['SMA 200'], label='SMA 200', alpha=0.35)
    plt.scatter(stock_data.index, buy_signals, label='Buy Signal', marker='^', color='green')
    plt.scatter(stock_data.index, sell_signals, label='Sell Signal', marker='v', color='red')
    plt.title(f'{ticker.upper()} Close Price History with Buy & Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()