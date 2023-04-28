# Import dependencies
from pandas_datareader import DataReader
import numpy as np
import pandas as pd
import datetime

# Define the stock and index symbols
stock = 'MSFT'
index = '^GSPC'

# Define the start and end dates for the data
start_date = datetime.datetime.now() - datetime.timedelta(days=1826)
end_date = datetime.date.today()

# Get the time series data for the stock and index from Yahoo Finance
df_stock = DataReader(stock, 'yahoo', start_date, end_date)
df_index = DataReader(index, 'yahoo', start_date, end_date)

# Resample the data to monthly time series
df_stock_monthly = df_stock.resample('M').last()
df_index_monthly = df_index.resample('M').last()

# Combine the adjusted closing prices of the stock and index into one DataFrame
df_combined = pd.DataFrame({
    'stock_adj_close': df_stock_monthly['Adj Close'],
    'index_adj_close': df_index_monthly['Adj Close']
}, index=df_stock_monthly.index)

# Calculate the monthly returns of the stock and index
df_combined[['stock_returns', 'index_returns']] = df_combined[['stock_adj_close', 'index_adj_close']] / \
                                                  df_combined[['stock_adj_close', 'index_adj_close']].shift(1) - 1

# Remove the rows with missing data
df_combined = df_combined.dropna()

# Calculate the covariance matrix of the returns
cov_matrix = np.cov(df_combined['stock_returns'], df_combined['index_returns'])

# Calculate the beta and alpha of the stock
beta = cov_matrix[0, 1] / cov_matrix[1, 1]
alpha = np.mean(df_combined['stock_returns']) - beta * np.mean(df_combined['index_returns'])

# Calculate the R-squared value
y_pred = alpha + beta * df_combined['index_returns']
ss_res = np.sum(np.power(y_pred - df_combined['stock_returns'], 2))
ss_tot = cov_matrix[0, 0] * (len(df_combined) - 1)
r_squared = 1. - ss_res / ss_tot

# Calculate the 5-year volatility and 1-year momentum
volatility = np.sqrt(cov_matrix[0, 0])
momentum = np.prod(1 + df_combined['stock_returns'].tail(12).values) - 1

# Annualize the numbers
periods_per_year = 12.
alpha = alpha * periods_per_year
volatility = volatility * np.sqrt(periods_per_year)

# Print the results
print(f'Beta: {beta:.4f}')
print(f'Alpha: {alpha:.4f}')
print(f'R-squared: {r_squared:.4f}')
print(f'Volatility: {volatility:.4f}')
print(f'Momentum: {momentum:.4f}')

# Calculate the average volume of the stock over the last 60 days and print it
volume = df_stock['Volume']
average_volume = volume.tail(60).mean()
print(f'Average Volume: {average_volume:.2f}')