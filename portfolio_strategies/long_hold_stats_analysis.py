# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt
from scipy.stats import norm

# Function to download stock data
def download_stock_data(symbol, start, end):
    return yf.download(symbol, start, end)['Adj Close']

# Function to calculate investment statistics
def calculate_investment_stats(df, investment_amount, symbol):
    # Calculate number of shares bought and investment values
    shares = int(investment_amount / df.iloc[0])
    begin_value = round(shares * df.iloc[0], 2)
    current_value = round(shares * df.iloc[-1], 2)

    # Calculate daily returns and various statistics
    returns = df.pct_change().dropna()
    stats = {
        'mean': round(returns.mean() * 100, 2),
        'std_dev': round(returns.std() * 100, 2),
        'skew': round(returns.skew(), 2),
        'kurt': round(returns.kurtosis(), 2),
        'total_return': round((1 + returns).cumprod().iloc[-1], 4) * 100
    }
    return shares, begin_value, current_value, stats

# User inputs
symbol = input('Enter a ticker: ')
num_of_years = float(input('Enter the number of years: '))
investment_amount = 100000

# Calculate date range
start = dt.datetime.now() - dt.timedelta(days=int(365.25 * num_of_years))
end = dt.datetime.now()

# Download and process stock data
df = download_stock_data(symbol, start, end)
shares, begin_value, current_value, stats = calculate_investment_stats(df, investment_amount, symbol)

# Print statistics
print(f'\nNumber of Shares for {symbol}: {shares}')
print(f'Beginning Value: ${begin_value}')
print(f'Current Value: ${current_value}')
print(f"\nStatistics:\nMean: {stats['mean']}%\nStd. Dev: {stats['std_dev']}%\nSkew: {stats['skew']}\nKurt: {stats['kurt']}\nTotal Return: {stats['total_return']}%")

# Plotting returns and other statistics
plt.figure(figsize=(10, 6))
df.pct_change().plot(title=f'{symbol} Daily Returns')
plt.show()