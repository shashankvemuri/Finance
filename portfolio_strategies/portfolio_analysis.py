import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import datetime as dt

# Override yfinance with Pandas Datareader's Yahoo Finance API
yf.pdr_override()

def get_historical_prices(symbols, start_date, end_date):
    """Retrieve historical stock prices for specified symbols."""
    return yf.download(symbols, start=start_date, end=end_date)['Adj Close']

def calculate_daily_returns(prices):
    """Calculate daily returns from stock prices."""
    return np.log(prices / prices.shift(1))

def calculate_monthly_returns(daily_returns):
    """Calculate monthly returns from daily returns."""
    return np.exp(daily_returns.groupby(lambda date: date.month).sum()) - 1

def calculate_annual_returns(daily_returns):
    """Calculate annual returns from daily returns."""
    return np.exp(daily_returns.groupby(lambda date: date.year).sum()) - 1

def portfolio_variance(returns, weights=None):
    """Calculate the variance of a portfolio."""
    if weights is None:
        weights = np.ones(len(returns.columns)) / len(returns.columns)
    covariance_matrix = np.cov(returns.T)
    return np.dot(weights, np.dot(covariance_matrix, weights))

def sharpe_ratio(returns, weights=None, risk_free_rate=0.001):
    """Calculate the Sharpe ratio of a portfolio."""
    if weights is None:
        weights = np.ones(len(returns.columns)) / len(returns.columns)
    port_var = portfolio_variance(returns, weights)
    port_return = np.dot(returns.mean(), weights)
    return (port_return - risk_free_rate) / np.sqrt(port_var)

# Example usage
symbols = ['AAPL', 'MSFT', 'GOOGL']
start_date = dt.datetime.now() - dt.timedelta(days=365*5)
end_date = dt.datetime.now()

# Fetch historical data
historical_prices = get_historical_prices(symbols, start_date, end_date)

# Calculate returns
daily_returns = calculate_daily_returns(historical_prices)
monthly_returns = calculate_monthly_returns(daily_returns)
annual_returns = calculate_annual_returns(daily_returns)

# Calculate portfolio metrics
portfolio_variance = portfolio_variance(annual_returns)
portfolio_sharpe_ratio = sharpe_ratio(daily_returns)

# Display results
print(f"Portfolio Variance: {portfolio_variance}")
print(f"Portfolio Sharpe Ratio: {portfolio_sharpe_ratio}")

# Plot historical prices
plt.figure(figsize=(10, 6))
historical_prices.plot()
plt.title("Historical Prices")
plt.xlabel("Date")
plt.ylabel("Adjusted Closing Price")
plt.legend(symbols)
plt.show()