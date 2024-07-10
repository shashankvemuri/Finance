# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
from sklearn.decomposition import PCA
from pandas_datareader import data as pdr
from pylab import rcParams

# Set parameters and retrieve stock tickers
num_years = 1
start_date = datetime.date.today() - datetime.timedelta(days=365.25 * num_years)
end_date = datetime.date.today()
tickers = yf.Tickers(' '.join(ti.tickers_sp500())).history(start=start_date, end=end_date)

# Calculate log differences of prices for market index and stocks
market_prices = pdr.get_data_yahoo('^GSPC', start_date, end_date)['Adj Close']
market_log_returns = np.log(market_prices).diff()
stock_prices = pdr.get_data_yahoo(tickers, start_date, end_date)['Adj Close']
stock_log_returns = np.log(stock_prices).diff()

# Plot daily returns of S&P 500 stocks
plt.figure(figsize=(15, 10))
plt.plot(stock_log_returns)
plt.title('Daily Returns of S&P 500 Stocks')
plt.show()

# Plot cumulative returns of S&P 500 stocks
cumulative_returns = stock_log_returns.cumsum().apply(np.exp)
plt.figure(figsize=(15, 10))
plt.plot(cumulative_returns)
plt.title('Cumulative Returns of S&P 500 Stocks')
plt.show()

# Perform PCA on stock returns
pca = PCA(n_components=1)
pca.fit(stock_log_returns.fillna(0))
pc1 = pd.Series(index=stock_log_returns.columns, data=pca.components_[0])

# Plot the first principal component
plt.figure(figsize=(15, 10))
plt.plot(pc1)
plt.title('First Principal Component of S&P 500 Stocks')
plt.show()

# Calculate weights for PCA portfolio and compare with market index
weights = abs(pc1) / sum(abs(pc1))
pca_portfolio_returns = (weights * stock_log_returns).sum(axis=1)
combined_returns = pd.concat([pca_portfolio_returns, market_log_returns], axis=1)
combined_returns.columns = ['PCA Portfolio', 'S&P 500']
cumulative_combined_returns = combined_returns.cumsum().apply(np.exp)

# Plot PCA portfolio vs S&P 500
plt.figure(figsize=(15, 10))
plt.plot(cumulative_combined_returns)
plt.title('PCA Portfolio vs S&P 500')
plt.legend(['PCA Portfolio', 'S&P 500'])
plt.show()

# Plot stocks with most and least significant PCA weights
fig, ax = plt.subplots(2, 1, figsize=(15, 10))
pc1.nsmallest(10).plot.bar(ax=ax[0], color='red', title='Stocks with Most Negative PCA Weights')
pc1.nlargest(10).plot.bar(ax=ax[1], color='green', title='Stocks with Most Positive PCA Weights')
plt.show()
