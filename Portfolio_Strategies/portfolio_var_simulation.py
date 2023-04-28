import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as web
from matplotlib.ticker import FuncFormatter
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from matplotlib.ticker import FuncFormatter
from pypfopt import objective_functions, base_optimizer
from scipy.stats import norm
import math
import datetime as dt

# List of tickers to analyze
tickers = ['GOOGL','FB','AAPL','NFLX','AMZN']
# Number of days (steps or trading days in this case)
Time=1440 
# Portfolio value
pvalue = 1000 

# Number of years of data to analyze
num_of_years = 3
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 

# Create a dataframe of adjusted closing prices for each stock
length = len(tickers)
price_data = []
for ticker in range(length):
   prices = web.DataReader(tickers[ticker], start = start_date, end = end_date, data_source='yahoo')
   price_data.append(prices[['Adj Close']])
df_stocks = pd.concat(price_data, axis=1)
df_stocks.columns=tickers

# Calculate the expected returns and covariance matrix
mu = expected_returns.mean_historical_return(df_stocks)
Sigma = risk_models.sample_cov(df_stocks)

# Use the EfficientFrontier class to optimize the portfolio weights
ef = EfficientFrontier(mu, Sigma, weight_bounds=(0,1)) 
sharpe_pfolio = ef.max_sharpe() 
sharpe_pwt = ef.clean_weights()
print(sharpe_pwt)

# Calculate VaR for the portfolio
ticker_rx2 = []
sh_wt = list(sharpe_pwt.values())
sh_wt = np.array(sh_wt)

# Calculate cumulative returns for each stock
for a in range(length):
    ticker_rx = df_stocks[[tickers[a]]].pct_change()
    ticker_rx = (ticker_rx+1).cumprod()
    ticker_rx2.append(ticker_rx[[tickers[a]]])
ticker_final = pd.concat(ticker_rx2,axis=1)

# Plot the cumulative returns of all stocks
for i, col in enumerate(ticker_final.columns):
    ticker_final[col].plot()
plt.title('Cumulative Returns')
plt.xticks(rotation=80)
plt.legend(ticker_final.columns)
plt.subplots()
plt.show()

# Calculate the latest returns and portfolio value
pret = []
pre1 = []
price = []
for x in range(length):
    pret.append(ticker_final.iloc[[-1],[x]])
    price.append((df_stocks.iloc[[-1],[x]]))
pre1 = pd.concat(pret,axis=1)
pre1 = np.array(pre1)
price = pd.concat(price,axis=1)
varsigma = pre1.std()
ex_rtn = pre1.dot(sh_wt)
price = price.dot(sh_wt) 

# Calculate the range of returns in a day
daily_returns = []
for i in range(10000): 
    daily_return = (np.random.normal(ex_rtn/Time,varsigma/math.sqrt(Time),Time))
    daily_returns.append(daily_return)

# Plot the range of returns in a day with 5th, 95th, and mean percentiles
plt.plot(daily_returns)
plt.title(f'Range of returns in a day of {Time} minutes')
plt.axhline(np.percentile(daily_returns,5), color='r', linestyle='dashed', linewidth=1)
plt.axhline(np.percentile(daily_returns,95), color='g', linestyle='dashed', linewidth=1)
plt.axhline(np.mean(daily_returns), color='b', linestyle='solid', linewidth=1)
plt.subplots()
plt.show()

# Plot histogram of daily returns with 5th, 95th, and mean percentiles
plt.hist(daily_returns,bins=15)
plt.axvline(np.percentile(daily_returns,5), color='r', linestyle='dashed', linewidth=2)
plt.axvline(np.percentile(daily_returns,95), color='r', linestyle='dashed', linewidth=2)
plt.subplots()
plt.show()

# Print findings
print(np.percentile(daily_returns,5),np.percentile(daily_returns,95))
print('$Amount required to cover minimum losses for one day is ' + str(pvalue* - np.percentile(daily_returns,5)))