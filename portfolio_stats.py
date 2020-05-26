import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
from scipy import stats
import seaborn as sns
import datetime

start_date = datetime.datetime(1984,1,1)
end_date = datetime.date.today()

# Create a list of tickers and weights
tickers = ['WMT', 'M', 'AAPL', 'TWLO', 'MRK']
wts = [0.1,0.2,0.25,0.25,0.2]

price_data = web.get_data_yahoo(tickers, start_date, end_date)
price_data = price_data['Adj Close']

ret_data = price_data.pct_change()[1:]

port_ret = (ret_data * wts).sum(axis = 1)

benchmark_price = web.get_data_yahoo('SPY', start_date, end_date)
                               
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
print("The portfolio alpha is", round(alpha,5))