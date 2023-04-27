# Import dependencies
import datetime
from functools import reduce
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
import yfinance as yf
from pandas_datareader import DataReader

sns.set(style='darkgrid', context='talk', palette='Dark2')

# Define the number of years to analyze
num_of_years = 3

# Calculate the start and end dates for the analysis
start = datetime.datetime.now() - datetime.timedelta(int(365.25 * num_of_years))
end = datetime.datetime.now()

# Define a date formatter
date_format = mdates.DateFormatter('%m/%y')

# Define the tickers to analyze
tickers = ['TSLA', 'AAPL', 'AMZN', 'NFLX']

# Retrieve the stock prices for the selected tickers
df = DataReader(tickers, 'yahoo', start, end)['Close']

# Calculate the rolling average for the short term and long term windows
short_rolling_mean = df.rolling(window=20).mean()
long_rolling_mean = df.rolling(window=100).mean()

# Calculate the Exponential Moving Average (EMA) for a 20-day window
ema_short = df.ewm(span=20, adjust=False).mean()

# Calculate the trading position for each asset based on the difference between the closing price and the EMA series
trade_pos_raw = df - ema_short

# Calculate the fixed weight of each asset (1/3 due to three assets)
fixed_weight = 1 / 3

# Calculate the trade position difference sign (1 if x > 0; -1 if x < 0) and multiply by the fixed weight of assets
trade_positions = trade_pos_raw.apply(np.sign) * fixed_weight

# Lag trading signals by a day (assuming that we traded at close of day t0 so we will have a long position on day t0+1)
trading_pos_final = trade_positions.shift(1)

# Calculate the logarithmic returns for each asset
asset_log_returns = np.log(df).diff()

# Calculate the logarithmic returns for each asset weighted by the trading positions
weighted_asset_log_returns = trading_pos_final * asset_log_returns

# Calculate the cumulative logarithmic returns for the portfolio
cumul_asset_log_returns = weighted_asset_log_returns.cumsum()

# Calculate the cumulative relative returns for the portfolio
cumul_asset_relative_returns = np.exp(cumul_asset_log_returns) - 1

# Plot the cumulative logarithmic returns for the asset portfolio and the total relative returns
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10))
for c in asset_log_returns:
    ax1.plot(cumul_asset_relative_returns.index, cumul_asset_relative_returns[c], label=str(c))
ax1.set_ylabel('Cumulative Log Returns')
ax1.legend(loc='best')
ax1.xaxis.set_major_formatter(date_format)
ax1.set_title('Cumulative', fontweight='bold')
for c in asset_log_returns:
    ax2.plot(cumul_asset_relative_returns.index, 100 * cumul_asset_relative_returns[c], label=str(c))
ax2.set_ylabel('Total Relative Returns (%)')
ax2.legend(loc='best')
ax2.xaxis.set_major_formatter(date_format)
ax2.set_title('Total Relative', fontweight='bold')
plt.tight_layout()

# Calculate the exact and approximate cumulative relative returns for the portfolio
cumul_relative_return_exact = cumul_asset_relative_returns.sum(axis=1)
cumul_log_return = cumul_asset_log_returns.sum(axis=1)
cumul_relative_return_appx = np.exp(cumul_log_return) - 1

# Plot Exact and Approximate equity curves
fig, ax = plt.subplots(figsize = (20, 10))
ax.plot(cumul_relative_return_exact.index, 100*cumul_relative_return_exact, label = 'Exact')
ax.plot(cumul_relative_return_appx.index, 100*cumul_relative_return_appx, label = 'Appx.')

ax.set_ylabel('Total Cumulative Relative Returns (%)')
ax.legend(loc = 'upper left')
ax.xaxis.set_major_formatter(date_format)

# Define a function to print lifetime total portfolio returns and average yearly returns
def print_yearly_statistics(portfolio_cumulative_relative_returns, days_per_year = 52*num_of_years):
    
    # Take final data point as the most recent total return to portfolio
    total_portfolio_return = portfolio_cumulative_relative_returns[-1]
    # Average portfolio return with compound return assumption
    average_yearly_return = (1 + total_portfolio_return)**(1/num_of_years) - 1
    
    print('Total portfolio return is: ' + '{:5.2f}'.format(100*total_portfolio_return)+'%')
    print('Average yearly return is: ' + '{:5.2f}'.format(100*average_yearly_return) + '%')

print_yearly_statistics(cumul_relative_return_exact)

# # Strategy Comparison with Simply Buy-and-Hold Strategy
simple_weights_matrix = pd.DataFrame(1/3, index = df.index, columns = df.columns)
simple_strategy_asset_log_returns = simple_weights_matrix * asset_log_returns
simple_cum_strategy_asset_log_returns = simple_strategy_asset_log_returns.cumsum()
simple_cum_strategy_asset_relative_returns = np.exp(simple_cum_strategy_asset_log_returns) - 1
simple_cum_relative_return_exact = simple_cum_strategy_asset_relative_returns.sum(axis = 1)

# Plot exponential moving average crossover strategy against simple buy and hold strategy
fig, ax = plt.subplots(figsize = (20, 10))
ax.plot(cumul_relative_return_exact.index, 100*cumul_relative_return_exact, label = 'EMA Strategy')
ax.plot(simple_cum_relative_return_exact.index, 100*simple_cum_relative_return_exact, label = 'Buy and Hold')
ax.set_ylabel('Total Cumulative Relative Returns (%)')
ax.legend(loc = 'best')
ax.xaxis.set_major_formatter(date_format)
plt.tight_layout()

print_yearly_statistics(simple_cum_relative_return_exact)