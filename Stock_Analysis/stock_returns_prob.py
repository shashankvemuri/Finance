import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days = 365*5)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)
returns = df['Adj Close'].pct_change()[1:].dropna()

import statistics as st
print('Mean of returns:', st.mean(returns))
print('Median of returns:', st.median(returns))
print('Median Low of returns:', st.median_low(returns))
print('Median High of returns:', st.median_high(returns))
print('Median Grouped of returns:', st.median_grouped(returns))
print('Mode of returns:', st.mode(returns))

from statistics import mode

print('Mode of returns:', mode(returns))
hist, bins = np.histogram(returns, 20) # Break data up into 20 bins
maxfreq = max(hist)

print('Mode of bins:', [(bins[i], bins[i+1]) for i, j in enumerate(hist) if j == maxfreq])

print('Arithmetic average of returns: ', returns.mean())

# Geometric mean
from scipy.stats.mstats import gmean
print('Geometric mean of stock:', gmean(returns))

ratios = returns + np.ones(len(returns))
R_G = gmean(ratios) - 1
print('Geometric mean of returns:', R_G)

print('Standard deviation of returns: ', returns.std())

T = len(returns)
init_price = df['Adj Close'][0]
final_price = df['Adj Close'][T]
print('Initial price:', init_price)
print('Final price:', final_price)
print('Final price as computed with R_G:', init_price*(1 + R_G)**T)

# Harmonic mean
print('Harmonic mean of returns:', len(returns)/np.sum(1.0/returns))

print('Skew:', stats.skew(returns))
print('Mean:', np.mean(returns))
print('Median:', np.median(returns))

plt.hist(returns, 30); 
plt.title(f'Histogram Returns for {symbol.upper()}')
plt.show()

# Plot some example distributions stock's returns
xs = np.linspace(-6,6, 1257)
normal = stats.norm.pdf(xs)
print('Excess kurtosis of leptokurtic distribution:', (stats.laplace.stats(returns)))
print('Excess kurtosis of mesokurtic distribution:', (stats.norm.stats(returns)))
print('Excess kurtosis of platykurtic distribution:', (stats.cosine.stats(returns)))

print("Excess kurtosis of returns: ", stats.kurtosis(returns))

from statsmodels.stats.stattools import jarque_bera
_, pvalue, _, _ = jarque_bera(returns)

if pvalue > 0.05:
    print('The returns are likely normal.')
else:
    print('The returns are likely not normal.')
