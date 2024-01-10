import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from scipy.optimize import fmin
import datetime as dt

# Function to download stock data and calculate annual returns
def annual_returns(symbols, start_date, end_date):
    df = yf.download(symbols, start_date, end_date)['Adj Close']
    log_rets = np.log(df / df.shift(1))
    return np.exp(log_rets.groupby(log_rets.index.year).sum()) - 1

# Function to calculate portfolio variance
def portfolio_var(returns, weights):
    cov_matrix = np.cov(returns.T)
    return np.dot(weights.T, np.dot(cov_matrix, weights))

# Function to calculate Sharpe ratio
def sharpe_ratio(returns, weights, rf_rate):
    portfolio_return = np.dot(returns.mean(), weights)
    portfolio_volatility = np.sqrt(portfolio_var(returns, weights))
    return (portfolio_return - rf_rate) / portfolio_volatility

# Function to optimize portfolio for maximum Sharpe ratio
def optimize_portfolio(returns, initial_weights, rf_rate):
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(len(initial_weights)))
    optimized = fmin(lambda x: -sharpe_ratio(returns, x, rf_rate), initial_weights, disp=False)
    return optimized

# Main function to execute the script
def main():
    symbols = ['FB', 'AAPL', 'MRK']
    start_date = dt.datetime.now() - dt.timedelta(days=365 * 7)
    end_date = dt.datetime.now()
    rf_rate = 0.003

    # Calculate annual returns
    returns = annual_returns(symbols, start_date, end_date)

    # Initialize equal weights
    initial_weights = np.ones(len(symbols)) / len(symbols)

    # Calculate equal weighted portfolio Sharpe ratio
    equal_weighted_sharpe = sharpe_ratio(returns, initial_weights, rf_rate)
    
    # Optimize portfolio
    optimal_weights = optimize_portfolio(returns, initial_weights, rf_rate)
    optimal_sharpe = sharpe_ratio(returns, optimal_weights, rf_rate)

    # Display results
    print("Equal Weighted Portfolio Sharpe Ratio:", equal_weighted_sharpe)
    print("Optimal Portfolio Weights:", optimal_weights)
    print("Optimal Portfolio Sharpe Ratio:", optimal_sharpe)

if __name__ == "__main__":
    main()