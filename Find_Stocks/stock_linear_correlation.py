# Libraries
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt

warnings.filterwarnings("ignore")
yf.pdr_override()

num_of_years = 1
start = dt.date.today() - dt.timedelta(days = int(365.25*num_of_years))
end = dt.date.today()

market = '^GSPC'
symbol1 = str(input('Enter a stock: '))
symbol2 = str(input('Enter another stock: '))
bench = yf.download(market, start=start, end=end)['Adj Close']
stock1 = yf.download(symbol1, start=start, end=end)['Adj Close']
stock2 = yf.download(symbol2, start=start, end=end)['Adj Close']

# plt.figure(figsize=(14,7))
# plt.scatter(stock1,stock2)
# plt.xlabel(symbol1)
# plt.ylabel(symbol2)
# plt.title('Stock prices from ' + str(start) + ' to ' + str(end))
# plt.show()

# plt.figure(figsize=(14,7))
# plt.scatter(stock1,bench)
# plt.xlabel(symbol1)
# plt.ylabel(market)
# plt.title('Stock prices from ' + str(start) + ' to ' + str(end))
# plt.show()

# plt.figure(figsize=(14,7))
# plt.scatter(stock2,bench)
# plt.xlabel(symbol2)
# plt.ylabel(market)
# plt.title('Stock prices from ' + str(start) + ' to ' + str(end))
# plt.show()

print("Correlation coefficients")
print(symbol1 + ' and ' + symbol2 + ':', np.corrcoef(stock1,stock2)[0,1])
print(symbol1 + ' and ' + market + ':', np.corrcoef(stock1,bench)[0,1])
print(market + ' and ' + symbol2 + ':', np.corrcoef(bench,stock2)[0,1])

# rolling_correlation = stock1.rolling(60).corr(stock2)
# plt.figure(figsize=(14,7))
# plt.plot(rolling_correlation)
# plt.xlabel('Day')
# plt.ylabel(f'60-day Rolling Correlation for {stock1} and {stock2}')
# plt.show()