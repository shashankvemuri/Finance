# Import dependencies
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
import datetime

# Prompt user for ticker symbol
ticker = input('Enter a ticker: ')

# Set index to S&P500 (SPY)
index = 'SPY'

# Set start date to 5 years ago from today
num_of_years = 5
start = datetime.date.today() - datetime.timedelta(days=int(365.25 * num_of_years))

# Download historical stock prices using yfinance library
yf_prices = yf.download([ticker], start=start)
prices = yf_prices['Adj Close']

# Plot stock prices and their distribution
fig, ax = plt.subplots(1, 2, figsize=(15, 10))
prices.plot(title=f'{ticker.upper()} Price', ax=ax[0], grid=True, linewidth=2)
prices.plot.hist(title=f'{ticker.upper()} Price Distribution', ax=ax[1], grid=True, bins=30)
plt.tight_layout()
plt.show()

# Calculate and plot stock returns and their distribution
rs = prices.apply(np.log).diff(1)
fig, ax = plt.subplots(1, 2, figsize=(15, 10))
rs.plot(title=f'{ticker.upper()} Returns', ax=ax[0], grid=True, linewidth=2)
rs.plot.hist(title=f'{ticker.upper()} Returns Distribution', ax=ax[1], grid=True, bins=30)
plt.tight_layout()
plt.show()

# Calculate rolling mean, standard deviation, skewness, and kurtosis of stock returns
window = 22
s1 = rs.rolling(window).mean()
s2 = rs.rolling(window).std()
s3 = rs.rolling(window).skew()
s4 = rs.rolling(window).kurt()

# Concatenate signals into a dataframe and plot each signal
signals = pd.concat([s1, s2, s3, s4], axis=1)
signals.columns = ['Mean', 'Std Dev', 'Skewness', 'Kurtosis']
signals.plot(subplots=True, figsize=(15, 10));
plt.tight_layout()
plt.show()

# Calculate volatility of S&P500 returns using rolling standard deviation
yf_prices = yf.download([index], start=start)
prices = yf_prices['Adj Close']
rs = prices.apply(np.log).diff(1)
vol = rs.rolling(window).std().dropna()

# Apply Gaussian Mixture model with two clusters to volatility data
labels = GaussianMixture(2).fit_predict(vol.values.reshape(-1, 1))
prices = prices.reindex(vol.index)

# Plot two different volatility regimes using Gaussian Mixture model
plt.subplots()
prices[labels == 0].plot(style='bo', alpha=0.2)
prices[labels == 1].plot(style='ro', alpha=0.2)
plt.title(f'{index} Volatility Regimes (Gaussian Mixture)')
plt.tight_layout()
plt.show()