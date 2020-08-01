import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
import datetime

ticker = input('Enter a ticker: ')
index = 'SPY'

num_of_years = 5
start = datetime.date.today() - datetime.timedelta(days = int(365.25*num_of_years))

yf_prices = yf.download([ticker], start=start)
prices = yf_prices['Adj Close']

subplots_ratio = dict(width_ratios=[3,2], height_ratios=[1])
fig, ax = plt.subplots(1,2, gridspec_kw=subplots_ratio, figsize=(15,10))
prices.plot(title=f'{ticker.upper()} Price', ax=ax[0], grid=True, linewidth=2)
prices.plot.hist(title=f'{ticker.upper()} Price Distribution', ax=ax[1], grid=True, bins=30)
plt.tight_layout()
plt.show()

rs = prices.apply(np.log).diff(1)
subplots_ratio = dict(width_ratios=[3,2], height_ratios=[1])
fig, ax = plt.subplots(1,2, gridspec_kw=subplots_ratio, figsize=(15,10))
rs.plot(title=f'{ticker.upper()} Returns', ax=ax[0], grid=True, linewidth=2)
rs.plot.hist(title=f'{ticker.upper()} Returns Distribution', ax=ax[1], grid=True, bins=30)
plt.tight_layout()
plt.show()

w = 22
s1 = rs.rolling(w).mean()
s2 = rs.rolling(w).std()
s3 = rs.rolling(w).skew()
s4 = rs.rolling(w).kurt()

signals = pd.concat([s1, s2, s3, s4], axis=1)
signals.columns = ['mean', 'std dev', 'skew', 'kurtosis']
signals.plot(subplots=True, figsize=(15,10));
plt.tight_layout()
plt.show()

yf_prices = yf.download([index], start=start)
prices = yf_prices['Adj Close']
rs = prices.apply(np.log).diff(1)

w = 22
vol = rs.rolling(w).std()
vol = vol.dropna()

labels = GaussianMixture(2).fit_predict(vol.values.reshape(-1,1))
prices = prices.reindex(vol.index)
plt.subplots()
prices[labels==0].plot(style='bo', alpha=0.2)
prices[labels==1].plot(style='ro', alpha=0.2)
plt.title(f'{index} Volatility Regimes (Gaussian Mixture)')
plt.tight_layout()
plt.show()