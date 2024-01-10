import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt

# Function to download stock data from Yahoo Finance
def get_stock_data(ticker):
    df = pdr.get_data_yahoo(ticker)
    df = df[['Adj Close']]
    return df

# Function to add Bollinger Bands to DataFrame
def add_bollinger_bands(df, window_size=20, num_std_dev=2):
    df['SMA'] = df['Adj Close'].rolling(window=window_size).mean()
    df['Upper Band'] = df['SMA'] + (df['Adj Close'].rolling(window=window_size).std() * num_std_dev)
    df['Lower Band'] = df['SMA'] - (df['Adj Close'].rolling(window=window_size).std() * num_std_dev)
    return df

# Function to plot stock prices with Bollinger Bands
def plot_with_bollinger_bands(df, ticker):
    plt.figure(figsize=(12,6))
    plt.plot(df['Adj Close'], label=f'{ticker} Adjusted Close', color='blue')
    plt.plot(df['SMA'], label='20 Day SMA', color='orange')
    plt.plot(df['Upper Band'], label='Upper Bollinger Band', color='green')
    plt.plot(df['Lower Band'], label='Lower Bollinger Band', color='red')
    plt.title(f'{ticker} Stock Price with Bollinger Bands')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

# Main function to execute the script
def main():
    ticker = input("Enter stock ticker: ")
    df = get_stock_data(ticker)
    df = add_bollinger_bands(df)
    plot_with_bollinger_bands(df, ticker)

if __name__ == "__main__":
    main()