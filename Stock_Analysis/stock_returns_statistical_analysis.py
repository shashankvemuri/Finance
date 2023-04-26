# Import dependencies
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Set yfinance override to True to prevent issues with pandas datareader
yf.pdr_override()

# Set the symbol and date range to be used for data retrieval
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days=365*5)
end = dt.date.today()

# Read data from Yahoo Finance using yfinance
df = yf.download(symbol, start, end)

# Calculate daily returns based on the 'Adj Close' column of the dataframe
returns = df['Adj Close'].pct_change()[1:].dropna()

# Calculate various statistics for the returns
mean_returns = np.mean(returns)
median_returns = np.median(returns)
mode_returns = stats.mode(returns)[0][0]
hist, bins = np.histogram(returns, 20)  # Break data up into 20 bins
maxfreq = max(hist)
mode_bins = [(bins[i], bins[i+1]) for i, j in enumerate(hist) if j == maxfreq]
arithmetic_mean_returns = returns.mean()
geometric_mean_returns = stats.gmean(returns)
standard_deviation_returns = returns.std()
harmonic_mean_returns = len(returns) / np.sum(1.0/returns)
skewness_returns = stats.skew(returns)
kurtosis_returns = stats.kurtosis(returns)
jarque_bera_results = stats.jarque_bera(returns)
is_normal = jarque_bera_results[1] > 0.05  # compare p-value to 0.05 significance level

# Print out the results of the calculations
print('Mean of returns:', mean_returns)
print('Median of returns:', median_returns)
print('Mode of returns:', mode_returns)
print('Mode of bins:', mode_bins)
print('Arithmetic average of returns: ', arithmetic_mean_returns)
print('Geometric mean of returns:', geometric_mean_returns)
print('Standard deviation of returns: ', standard_deviation_returns)
print('Harmonic mean of returns:', harmonic_mean_returns)
print('Skew:', skewness_returns)
print('Kurtosis:', kurtosis_returns)
print("Jarque-Bera p-value:", jarque_bera_results[1])
print('Are the returns normal?', is_normal)

# Plot a histogram of the returns
plt.hist(returns, 30)
plt.title(f'Histogram of Returns for {symbol.upper()}')
plt.show()

# Plot some example distributions of the stock's returns
xs = np.linspace(-6, 6, 1257)
normal = stats.norm.pdf(xs)
leptokurtic = stats.laplace.stats(returns)
mesokurtic = stats.norm.stats(returns)
platykurtic = stats.cosine.stats(returns)
print('Excess kurtosis of leptokurtic distribution:', leptokurtic)
print('Excess kurtosis of mesokurtic distribution:', mesokurtic)
print('Excess kurtosis of platykurtic distribution:', platykurtic)
print("Excess kurtosis of returns: ", kurtosis_returns)