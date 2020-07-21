# Libraries
import numpy as np
import warnings
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
from yahoo_fin import stock_info as si
import pandas as pd
import scipy.stats as stats

warnings.filterwarnings("ignore")
yf.pdr_override()

num_of_years = 1
start = dt.date.today() - dt.timedelta(days = int(365.25*num_of_years))
end = dt.date.today()

tickers = si.tickers_dow()
dataset = pd.read_csv('/Users/shashank/Documents/Code/Python/Research/s&p500/betaDistribution/S&P500_stock_prices.csv', index_col=0, parse_dates = True)

stocks_returns = np.log(dataset / dataset.shift(1))
cov_matrix = stocks_returns.cov()

print('Covariance Matrix')
cov_matrix = stocks_returns.cov()
print (cov_matrix)

print('\nCorrelation Matrix')
corr_matrix = stocks_returns.corr()
print (corr_matrix)