import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import pandas as pd
import datetime

# Fetch stock data from Yahoo Finance
def fetch_stock_data(ticker, start, end):
    return DataReader(ticker, 'yahoo', start, end)

# Calculate Fibonacci retracement levels
def fibonacci_levels(price_min, price_max):
    diff = price_max - price_min
    return {
        '0%': price_max,
        '23.6%': price_max - 0.236 * diff,
        '38.2%': price_max - 0.382 * diff,
        '61.8%': price_max - 0.618 * diff,
        '100%': price_min
    }

# Plot the stock data and Fibonacci levels
def plot_fibonacci_retracement(stock_data, fib_levels):
    fig, ax = plt.subplots()
    ax.plot(stock_data['Close'], color='black')

    for level, price in fib_levels.items():
        ax.axhline(y=price, color='blue', linestyle='--', label=f'{level} level at {price:.2f}')
    
    plt.title(f'{stock_ticker} Fibonacci Retracement')
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.legend()
    plt.show()

# Main program
if __name__ == '__main__':
    stock_ticker = 'AAPL'
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.date.today()

    stock_data = fetch_stock_data(stock_ticker, start_date, end_date)
    price_min = stock_data['Close'].min()
    price_max = stock_data['Close'].max()
    fib_levels = fibonacci_levels(price_min, price_max)

    plot_fibonacci_retracement(stock_data, fib_levels)