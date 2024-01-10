import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
from pandas_datareader import data as pdr
import numpy as np

# Setting plot style and context
sns.set(style='darkgrid', context='talk', palette='Dark2')

# Define the analysis period
num_of_years = 3
start = dt.datetime.now() - dt.timedelta(days=365.25 * num_of_years)
end = dt.datetime.now()

# Define tickers for analysis
tickers = ['TSLA', 'AAPL', 'AMZN', 'NFLX']

# Fetch stock data using Yahoo Finance
df = pdr.get_data_yahoo(tickers, start, end)['Close']

# Calculate moving averages
short_rolling = df.rolling(window=20).mean()
long_rolling = df.rolling(window=100).mean()
ema_short = df.ewm(span=20, adjust=False).mean()

# Determine trading position based on EMA
trade_positions_raw = df - ema_short
trade_positions = trade_positions_raw.apply(np.sign) / 3  # Equal weighting
trade_positions_final = trade_positions.shift(1)  # Shift to simulate next-day trading

# Calculate asset and portfolio returns
asset_log_returns = np.log(df).diff()
portfolio_log_returns = trade_positions_final * asset_log_returns
cumulative_portfolio_log_returns = portfolio_log_returns.cumsum()
cumulative_portfolio_relative_returns = np.exp(cumulative_portfolio_log_returns) - 1

# Plot cumulative returns
plt.figure(figsize=(20, 10))
for ticker in asset_log_returns:
    plt.plot(cumulative_portfolio_relative_returns.index, 100 * cumulative_portfolio_relative_returns[ticker], label=ticker)
plt.xlabel('Date')
plt.ylabel('Cumulative Log Returns (%)')
plt.legend(loc='best')
plt.show()

# Comparing exact and approximate cumulative returns
cumulative_return_exact = cumulative_portfolio_relative_returns.sum(axis=1)
cumulative_log_return = cumulative_portfolio_log_returns.sum(axis=1)
cumulative_return_approx = np.exp(cumulative_log_return) - 1

# Plot exact vs approximate returns
plt.figure(figsize=(20, 10))
plt.plot(cumulative_return_exact.index, 100 * cumulative_return_exact, label='Exact')
plt.plot(cumulative_return_approx.index, 100 * cumulative_return_approx, label='Approx')
plt.xlabel('Date')
plt.ylabel('Total Cumulative Relative Returns (%)')
plt.legend(loc='upper left')
plt.show()

# Function to print portfolio statistics
def print_portfolio_statistics(portfolio_returns, num_of_years):
    total_return = portfolio_returns[-1]
    avg_yearly_return = (1 + total_return) ** (1 / num_of_years) - 1
    print(f'Total Portfolio Return: {total_return * 100:.2f}%')
    print(f'Average Yearly Return: {avg_yearly_return * 100:.2f}%')

# Printing statistics for EMA crossover strategy
print_portfolio_statistics(cumulative_return_exact, num_of_years)