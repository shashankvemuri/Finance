# Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import yfinance as yf
from dateutil import relativedelta
import datetime as dt

# Override yfinance API to enable Pandas Datareader
yf.pdr_override()

# Function to get historical stock price data
def get_historical_prices(symbols, start_date, end_date):
    df = yf.download(symbols, start=start_date, end=end_date)['Adj Close']
    return df

# Example list of symbols to fetch historical data for
symbols = ['FB', 'JNJ', 'LMT']
start_date = dt.datetime.now() - dt.timedelta(days=365*7)
end_date = dt.datetime.now()

# Fetch historical closing prices for the given symbols and dates
closes = get_historical_prices(symbols, start_date, end_date)

# Function to calculate daily returns from price data
def calc_daily_returns(closes):
    return np.log(closes/closes.shift(1))

# Calculate daily returns from historical closing prices
daily_returns = calc_daily_returns(closes)

# Drop rows with NaN values
daily_returns = daily_returns.dropna()

# Function to calculate monthly returns from daily returns
def calc_monthly_returns(daily_returns):
    monthly = np.exp(daily_returns.groupby(lambda date: date.month).sum())-1
    return monthly

# Calculate monthly returns from daily returns
month_returns = calc_monthly_returns(daily_returns)

# Function to calculate annual returns from daily returns
def calc_annual_returns(daily_returns):
    grouped = np.exp(daily_returns.groupby(lambda date: date.year).sum())-1
    return grouped

# Calculate annual returns from daily returns
annual_returns = calc_annual_returns(daily_returns)

# Function to calculate portfolio variance
def calc_portfolio_var(returns, weights=None):
    if weights is None:
        weights = np.ones(returns.columns.size) / returns.columns.size
    sigma = np.cov(returns.T, ddof=0)
    var = (weights * sigma * weights.T).sum()
    return var

# Calculate portfolio variance from annual returns
portfolio_var = calc_portfolio_var(annual_returns)

# Function to calculate Sharpe ratio
def calc_sharpe_ratio(returns, weights=None, risk_free_rate=0.001):
    n = returns.columns.size
    if weights is None: 
        weights = np.ones(n)/n
    var = calc_portfolio_var(returns, weights)
    means = returns.mean()
    sharpe_ratio = (means.dot(weights) - risk_free_rate) / np.sqrt(var)
    return sharpe_ratio

# Calculate Sharpe ratio from daily returns
sharpe_ratio = calc_sharpe_ratio(daily_returns)