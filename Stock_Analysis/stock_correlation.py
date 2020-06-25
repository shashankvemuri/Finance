# # Stock Covariance & Correlations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# ## Two Securities Correlation

# input
symbols = ['AMD','INTC']
start = dt.date.today() - dt.timedelta(days = 365*7)
end = dt.date.today()

# Read data 
dataset = yf.download(symbols,start,end)['Adj Close']

# View Columns
dataset.head()

stocks_returns = np.log(dataset / dataset.shift(1))

AMD = stocks_returns['AMD'].var() 
INTC = stocks_returns['INTC'].var() 

AMD = stocks_returns['AMD'].var() * 250
INTC = stocks_returns['INTC'].var() * 250

cov_matrix = stocks_returns.cov()

print('Covariance Matrix')
cov_matrix = stocks_returns.cov()*250
print (cov_matrix)

print('\nCorrelation Matrix')
corr_matrix = stocks_returns.corr()*250
print (corr_matrix)

# ## Four Securities Correlation
# input
symbols = ['AAPL','MSFT','AMD','NVDA']
start = dt.date.today() - dt.timedelta(days = 365*7)
end = dt.date.today()

# Read data 
dataset = yf.download(symbols,start,end)['Adj Close']

stocks_returns = np.log(dataset / dataset.shift(1))

AAPL = stocks_returns['AAPL'].var() 
MSFT = stocks_returns['MSFT'].var() 
AMD = stocks_returns['AMD'].var() 
NVDA = stocks_returns['NVDA'].var() 

AAPL = stocks_returns['AAPL'].var() * 250
MSFT = stocks_returns['MSFT'].var() * 250 
AMD = stocks_returns['AMD'].var() * 250 
NVDA = stocks_returns['NVDA'].var() * 250 

cov_matrix = stocks_returns.cov()

print('Covariance Matrix')
cov_matrix = stocks_returns.cov()*250
print (cov_matrix)

print('\nCorrelation Matrix')
corr_matrix = stocks_returns.corr()*250
print(corr_matrix)