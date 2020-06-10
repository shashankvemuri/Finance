import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta

def get_historical_price(ticker, start_date, end_date):
    df = yf.download(ticker, start_date, end_date)['Adj Close']
    return df

symbols = ['FB','JNJ','LMT']
start = dt.datetime.now() - dt.timedelta(days = 365*7)
end = dt.datetime.now()

closes = get_historical_price(symbols, start, end)

def calc_daily_returns(closes):
    return np.log(closes/closes.shift(1))

daily_returns = calc_daily_returns(closes)
daily_returns = daily_returns.dropna()

def calc_month_returns(daily_returns):
    monthly = np.exp(daily_returns.groupby(lambda date: date.month).sum())-1
    return monthly

month_returns = calc_month_returns(daily_returns)

def calc_annual_returns(daily_returns):
    grouped = np.exp(daily_returns.groupby(lambda date: date.year).sum())-1
    return grouped

annual_returns = calc_annual_returns(daily_returns)

def calc_portfolio_var(returns, weights=None):
    if (weights is None):
        weights = np.ones(returns.columns.size) / returns.columns.size
    sigma = np.cov(returns.T,ddof=0)
    var = (weights * sigma * weights.T).sum()
    return var

calc_portfolio_var(annual_returns)

def Sharpe_ratio(returns, weights = None, risk_free_rate = 0.001):
    n = returns.columns.size
    if (weights is None): 
        weights = np.ones(n)/n
        var = calc_portfolio_var(returns, weights)
        means = returns.mean()
        sr = (means.dot(weights) - risk_free_rate)/np.sqrt(var)
        return sr

Sharpe_ratio(daily_returns)