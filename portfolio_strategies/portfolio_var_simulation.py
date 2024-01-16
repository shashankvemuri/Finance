import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as web
from matplotlib.ticker import FuncFormatter
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns
from scipy.stats import norm
import datetime as dt

# Define the tickers and time parameters
tickers = ['GOOGL', 'FB', 'AAPL', 'NFLX', 'AMZN']
Time = 1440  # Number of trading days in minutes
pvalue = 1000  # Portfolio value in dollars
num_of_years = 3
start_date = dt.datetime.now() - dt.timedelta(days=365.25 * num_of_years)
end_date = dt.datetime.now()

# Fetching and preparing stock data
price_data = [web.DataReader(ticker, start=start_date, end=end_date, data_source='yahoo')['Adj Close'] for ticker in tickers]
df_stocks = pd.concat(price_data, axis=1)
df_stocks.columns = tickers

# Calculating expected returns and covariance matrix
mu = expected_returns.mean_historical_return(df_stocks)
Sigma = risk_models.sample_cov(df_stocks)

# Portfolio Optimization using Efficient Frontier
ef = EfficientFrontier(mu, Sigma, weight_bounds=(0,1))
sharpe_pwt = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
print(cleaned_weights)

# Plotting Cumulative Returns of All Stocks
cum_returns = ((df_stocks.pct_change() + 1).cumprod() - 1)
cum_returns.plot(title='Cumulative Returns')
plt.xticks(rotation=80)
plt.legend(cum_returns.columns)
plt.show()

# Portfolio VaR Simulation
ticker_returns = cum_returns.pct_change().dropna()
weighted_returns = ticker_returns.dot(np.array(list(cleaned_weights.values())))
portfolio_return = weighted_returns.mean()
portfolio_vol = weighted_returns.std()

# Simulating daily returns for VAR calculation
simulated_daily_returns = [np.random.normal(portfolio_return / Time, portfolio_vol / np.sqrt(Time), Time) for _ in range(10000)]

# Plotting Range of Returns in a Day
plt.plot(simulated_daily_returns)
plt.title(f'Range of Returns in a Day of {Time} Minutes')
plt.axhline(np.percentile(simulated_daily_returns, 5), color='r', linestyle='dashed', linewidth=1)
plt.axhline(np.percentile(simulated_daily_returns, 95), color='g', linestyle='dashed', linewidth=1)
plt.axhline(np.mean(simulated_daily_returns), color='b', linestyle='solid', linewidth=1)
plt.show()

# Histogram of Daily Returns
plt.hist(simulated_daily_returns, bins=15)
plt.axvline(np.percentile(simulated_daily_returns, 5), color='r', linestyle='dashed', linewidth=2)
plt.axvline(np.percentile(simulated_daily_returns, 95), color='r', linestyle='dashed', linewidth=2)
plt.show()

# Printing VaR results
print(f"5th Percentile: {np.percentile(simulated_daily_returns, 5)}")
print(f"95th Percentile: {np.percentile(simulated_daily_returns, 95)}")
print(f"Amount required to cover minimum losses for one day: ${pvalue * -np.percentile(simulated_daily_returns, 5)}")