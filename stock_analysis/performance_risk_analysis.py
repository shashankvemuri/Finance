from pandas_datareader import DataReader
import numpy as np
import pandas as pd
import datetime

# Setting the stock and index symbols
stock = 'MSFT'
index = '^GSPC'

# Defining time range for data
start_date = datetime.datetime.now() - datetime.timedelta(days=1826)
end_date = datetime.date.today()

# Fetching data for the stock and S&P 500 index
df_stock = DataReader(stock, 'yahoo', start_date, end_date)
df_index = DataReader(index, 'yahoo', start_date, end_date)

# Resampling the data to a monthly time series
df_stock_monthly = df_stock['Adj Close'].resample('M').last()
df_index_monthly = df_index['Adj Close'].resample('M').last()

# Calculating monthly returns
stock_returns = df_stock_monthly.pct_change().dropna()
index_returns = df_index_monthly.pct_change().dropna()

# Computing Beta, Alpha, and R-squared
cov_matrix = np.cov(stock_returns, index_returns)
beta = cov_matrix[0, 1] / cov_matrix[1, 1]
alpha = np.mean(stock_returns) - beta * np.mean(index_returns)

y_pred = alpha + beta * index_returns
r_squared = 1 - np.sum((y_pred - stock_returns) ** 2) / np.sum((stock_returns - np.mean(stock_returns)) ** 2)

# Calculating Volatility and Momentum
volatility = np.std(stock_returns) * np.sqrt(12)  # Annualized volatility
momentum = np.prod(1 + stock_returns.tail(12)) - 1  # 1-year momentum

# Printing the results
print(f'Beta: {beta:.4f}')
print(f'Alpha: {alpha:.4f} (annualized)')
print(f'R-squared: {r_squared:.4f}')
print(f'Volatility: {volatility:.4f}')
print(f'1-Year Momentum: {momentum:.4f}')

# Calculating the average volume over the last 60 days
average_volume = df_stock['Volume'].tail(60).mean()
print(f'Average Volume (last 60 days): {average_volume:.2f}')