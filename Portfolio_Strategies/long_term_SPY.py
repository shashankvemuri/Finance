import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats.norm.pdf as normpdf
import seaborn as sns
from tabulate import tabulate
import math
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta

# input
symbol = 'SPY'
start = dt.datetime.now() - dt.timedelta(days = 365*12)
end = dt.datetime.now()

# Read data 
df = yf.download(symbol,start,end)['Adj Close']

delta = relativedelta.relativedelta(start,end)
print('How many years of investing?')
print('%s years' % delta.years)

# ### Starting Cash with 100k to invest in Bonds
Cash = 100000

print('Number of Shares:')
shares = int(Cash/df.iloc[0])
print('{}: {}'.format(symbol, shares))

print('Beginning Value:')
shares = int(Cash/df.iloc[0])
Begin_Value = round(shares * df.iloc[0], 2)
print('{}: ${}'.format(symbol, Begin_Value))

print('Current Value:')
shares = int(Cash/df.iloc[0])
Current_Value = round(shares * df.iloc[-1], 2)
print('{}: ${}'.format(symbol, Current_Value))

returns = df.pct_change().dropna()

# Calculate cumulative returns
daily_cum_ret=(1+returns).cumprod()
print(daily_cum_ret.tail())

# Print the mean
print("mean : ", returns.mean()*100)

# Print the standard deviation
print("Std. dev: ", returns.std()*100)

# Print the skewness
print("skew: ", returns.skew())

# Print the kurtosis
print("kurt: ", returns.kurtosis())

# Calculate total return and annualized return from price data 
total_return = (returns[-1] - returns[0]) / returns[0]
print(total_return)

# Annualize the total return over 12 year 
annualized_return = ((1+total_return)**(1/12))-1

# Calculate annualized volatility from the standard deviation
vol_port = returns.std() * np.sqrt(250)

# Calculate the Sharpe ratio 
rf = 0.001
sharpe_ratio = (annualized_return - rf) / vol_port
print(sharpe_ratio)

# Create a downside return column with the negative returns only
target = 0
downside_returns = returns.loc[returns < target]

# Calculate expected return and std dev of downside
expected_return = returns.mean()
down_stdev = downside_returns.std()

# Calculate the sortino ratio
rf = 0.01
sortino_ratio = (expected_return - rf)/down_stdev

# Print the results
print("Expected return: ", expected_return*100)
print('-' * 50)
print("Downside risk:")
print(down_stdev*100)
print('-' * 50)
print("Sortino ratio:")
print(sortino_ratio)

# Calculate the max value 
roll_max = returns.rolling(center=False,min_periods=1,window=252).max()

# Calculate the daily draw-down relative to the max
daily_draw_down = returns/roll_max - 1.0

# Calculate the minimum (negative) daily draw-down
max_daily_draw_down = daily_draw_down.rolling(center=False,min_periods=1,window=252).min()

# Plot the results
plt.figure(figsize=(15,15))
plt.plot(returns.index, daily_draw_down, label='Daily drawdown')
plt.plot(returns.index, max_daily_draw_down, label='Maximum daily drawdown in time-window')
plt.legend()
plt.show()

# Box plot
returns.plot(kind='box')
plt.show()

print("Stock returns: ")
print(returns.mean())
print('-' * 50)
print("Stock risk:")
print(returns.std())

rf = 0.001
Sharpe_Ratio = ((returns.mean() - rf) / returns.std()) * np.sqrt(252)
print('Sharpe Ratio: ', Sharpe_Ratio)

# ### Value-at-Risk 99% Confidence
# 99% confidence interval
# 0.01 empirical quantile of daily returns
var99 = round((returns).quantile(0.01), 3)

print('Value at Risk (99% confidence)')
print(var99)

# the percent value of the 5th quantile
print('Percent Value-at-Risk of the 5th quantile')
var_1_perc = round(np.quantile(var99, 0.01), 3)
print("{:.1f}%".format(-var_1_perc*100))

print('Value-at-Risk of 99% for 100,000 investment')
print("${}".format(int(-var99 * 100000)))

# ### Value-at-Risk 95% Confidence
# 95% confidence interval
# 0.05 empirical quantile of daily returns
var95 = round((returns).quantile(0.05), 3)

print('Value at Risk (95% confidence)')
print(var95)

print('Percent Value-at-Risk of the 5th quantile')
print("{:.1f}%".format(-var95*100))

# VaR for 100,000 investment
print('Value-at-Risk of 99% for 100,000 investment')
var_100k = "${}".format(int(-var95 * 100000))
print("${}".format(int(-var95 * 100000)))

mean = np.mean(returns)
std_dev = np.std(returns)

returns.hist(bins=50, density=True, histtype='stepfilled', alpha=0.5)
x = np.linspace(mean - 3*std_dev, mean + 3*std_dev, 100)
plt.plot(x, normpdf(x, mean, std_dev), "r")
plt.title('Histogram of Returns')
plt.show()

VaR_90 = norm.ppf(1-0.9, mean, std_dev)
VaR_95 = norm.ppf(1-0.95, mean, std_dev)
VaR_99 = norm.ppf(1-0.99, mean, std_dev)

print(tabulate([['90%', VaR_90], ['95%', VaR_95], ['99%', VaR_99]], headers=['Confidence Level', 'Value at Risk']))
