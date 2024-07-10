import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Function to download stock data
def download_stock_data(ticker, start_date, end_date):
    return yf.download(ticker, start_date, end_date)

# Function to calculate moving averages
def calculate_moving_averages(data, windows):
    for window in windows:
        data[f'SMA_{window}'] = data['Adj Close'].rolling(window).mean()
    return data

# Main function
def main():
    symbol = 'NIO'
    start_date = dt.date.today() - dt.timedelta(days=365 * 10)  # 10 years ago
    end_date = dt.date.today()

    # Download and calculate moving averages
    stock_data = download_stock_data(symbol, start_date, end_date)
    windows = [20, 40, 80]
    stock_data = calculate_moving_averages(stock_data, windows)

    # Plotting
    plt.figure(figsize=(16,9))
    plt.plot(stock_data['Adj Close'], label='Price', color='black')
    for window in windows:
        plt.plot(stock_data[f'SMA_{window}'], label=f'{window}-days SMA')
    plt.legend(loc='best')
    plt.ylabel('Price')
    plt.title(f'{symbol} - Big Three Trading Strategy')
    plt.show()

if __name__ == "__main__":
    main()