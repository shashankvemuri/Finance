import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
import numpy as np

ticker = 'TSLA'
start = '2019-01-18'
end = '2020-01-18'

stock = web.DataReader(ticker,'yahoo', start, end)
stock = stock.dropna(how='any')

stock.head()

stock['Adj Close'].plot(grid = True)

stock['ret'] = stock['Adj Close'].pct_change()
stock['ret'].plot(grid=True)

stock['20d'] = stock['Adj Close'].rolling(window=20, center=False).mean()
stock['20d'].plot(grid=True)

#Populates the time period number in stock under head t
stock['t'] = range (1,len(stock)+1)
#Computes t squared, tXD(t) and n
stock['sqr t']=stock['t']**2
stock['tXD']=stock['t']*stock['Adj Close']
n=len(stock)
#Computes slope and intercept
slope = (n*stock['tXD'].sum() - stock['t'].sum()*stock['Adj Close'].sum())/(n*stock['sqr t'].sum() - (stock['t'].sum())**2)
intercept = (stock['Adj Close'].sum()*stock['sqr t'].sum() - stock['t'].sum()*stock['tXD'].sum())/(n*stock['sqr t'].sum() - (stock['t'].sum())**2)
print ('The slope of the linear trend (b) is: ', slope)
print ('The intercept (a) is: ', intercept)

#Computes the forecasted values
stock['forecast'] = intercept + slope*stock['t']
#Computes the error
stock['error'] = stock['Adj Close'] - stock['forecast']
mean_error=stock['error'].mean()
print ('The mean error is: ', mean_error)