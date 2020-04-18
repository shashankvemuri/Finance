import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
from scipy import stats
import seaborn as sns

# Create a list of tickers and weights
tickers = ['WMT', 'M', 'AAPL', 'TWLO', 'MRCK','TGT', 'NI', 'FSUVX', 'NKE', 'AXP', 'PG', 'SOXX', 'SBUX', 'KO', 'MDLZ', 'COST', 'FB']
wts = [0.1,0.2,0.25,0.25,0.2]

price_data = web.get_data_yahoo(tickers,
                               start = '2019-09-04',
                               end = '2019-11-04')
price_data = price_data['Adj Close']

ret_data = price_data.pct_change()[1:]

port_ret = (ret_data * wts).sum(axis = 1)

benchmark_price = web.get_data_yahoo('SPY',
                               start = '2013-01-01',
                               end = '2018-03-01')
                               
benchmark_ret = benchmark_price["Adj Close"].pct_change()[1:]

sns.regplot(benchmark_ret.values,
port_ret.values)
plt.xlabel("Benchmark Returns")
plt.ylabel("Portfolio Returns")
plt.title("Portfolio Returns vs Benchmark Returns")
plt.show()


(beta, alpha) = stats.linregress(benchmark_ret.values,
                port_ret.values)[0:2]
                
print("The portfolio beta is", round(beta, 4))
## The portfolio beta is 0.9329
print("The portfolio beta is", round(alpha,5))