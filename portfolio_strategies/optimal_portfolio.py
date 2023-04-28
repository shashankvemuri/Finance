# Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from scipy.optimize import fmin
import datetime as dt

# Set yfinance to download data faster
yf.pdr_override()

# Define the input variables
symbols = ['FB', 'AAPL', 'MRK']
start_date = dt.datetime.now() - dt.timedelta(days=365*7)
end_date = dt.datetime.now()
rf_rate = 0.003

def annual_returns(symbols, start_date, end_date):
    # Download historical stock prices for the specified symbols
    df = yf.download(symbols, start_date, end_date)['Adj Close']
    # Calculate the daily log returns
    log_rets = np.log(df) - np.log(df.shift(1))
    # Convert the daily log returns to annual returns
    yearly_returns = np.exp(log_rets.groupby(log_rets.index.year).sum()) - 1
    yearly_returns.columns = symbols
    return yearly_returns

def portfolio_var(returns, weights):
    # Calculate the covariance matrix and the volatility vector
    cov_matrix = np.cov(returns.T)
    volatilities = np.sqrt(np.diag(cov_matrix))
    # Calculate the portfolio variance
    portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
    return portfolio_var

def sharpe_ratio(returns, weights, rf_rate):
    # Calculate the portfolio return and the portfolio volatility
    portfolio_return = np.dot(returns, weights)
    portfolio_volatility = np.sqrt(portfolio_var(returns, weights))
    # Calculate the Sharpe ratio
    sharpe_ratio = (portfolio_return - rf_rate) / portfolio_volatility
    return sharpe_ratio

def negative_sharpe_n_minus_1_stock(weights, returns, rf_rate):
    # Define the weights for the remaining stocks
    remaining_weight = 1 - np.sum(weights)
    remaining_weights = np.append(weights, remaining_weight)
    # Calculate the negative Sharpe ratio
    return -sharpe_ratio(returns, remaining_weights, rf_rate)

# Calculate the annual returns for the specified symbols
returns = annual_returns(symbols, start_date, end_date)

# Calculate the Sharpe ratio for an equal-weighted portfolio
equal_weights = np.ones(len(symbols)) / len(symbols)
equal_weighted_sharpe_ratio = sharpe_ratio(returns, equal_weights, rf_rate)

# Calculate the optimal weights and the corresponding Sharpe ratio
optimal_weights = fmin(negative_sharpe_n_minus_1_stock, np.ones(len(symbols)-1, dtype=float) / len(symbols))
optimal_weighted_sharpe_ratio = sharpe_ratio(returns, optimal_weights, rf_rate)

print('Symbols: ', symbols)
print('Equal Weighted Portfolio: ')
print('Weights: ', equal_weights)
print('Sharpe Ratio: ', equal_weighted_sharpe_ratio)
print('Optimal Weighted Portfolio: ')
print('Weights: ', optimal_weights)
print('Sharpe Ratio: ', optimal_weighted_sharpe_ratio)