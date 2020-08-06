import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sns
from tabulate import tabulate
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta

# input
symbol = input('Enter a ticker: ')
num_of_years = float(input('Enter the number of years: '))

start = dt.datetime.now() - dt.timedelta(days = int(365.25*num_of_years))
end = dt.datetime.now()

# Read data 
df = yf.download(symbol,start,end)['Adj Close']

delta = relativedelta.relativedelta(start,end)
print('How many years of investing?')
print('%s years' % num_of_years)

# ### Starting Cash with 100k to invest in Bonds
Cash = 100000

print('\nNumber of Shares:')
shares = int(Cash/df.iloc[0])
print('{}: {}'.format(symbol, shares))

print('\nBeginning Value:')
shares = int(Cash/df.iloc[0])
Begin_Value = round(shares * df.iloc[0], 2)
print('{}: ${}'.format(symbol, Begin_Value))

print('\nCurrent Value:')
shares = int(Cash/df.iloc[0])
Current_Value = round(shares * df.iloc[-1], 2)
print('{}: ${}'.format(symbol, Current_Value))

returns = df.pct_change().dropna()

# Calculate cumulative returns
daily_cum_ret=(1+returns).cumprod()

# Print the mean
print("\nmean: " + str(round(returns.mean()*100, 2)))

# Print the standard deviation
print("Std. dev: " + str(round(returns.std()*100, 2)))

# Print the skewness
print("skew: " + str(round(returns.skew(), 2)))

# Print the kurtosis
print("kurt: " + str(round(returns.kurtosis(), 2)))

# Calculate total return and annualized return from price data 
total_return = round(daily_cum_ret.tolist()[-1], 4) * 100
print('\nTotal Return: ' + str(total_return) + '%')

# Annualize the total return over 12 year 
annualized_return = ((1+total_return)**(1/12))-1

# Calculate annualized volatility from the standard deviation
vol_port = returns.std() * np.sqrt(250)

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
print('-' * 50)
print("Expected return: " + str(round(expected_return*100, 2)))
print('-' * 50)
print("Downside risk: " + str(round(down_stdev*100, 2)))
print('-' * 50)
print("Sortino ratio: " + str(round(sortino_ratio, 2)))
print('-' * 50)

# Calculate the max value 
roll_max = returns.rolling(center=False,min_periods=1,window=252).max()

# Calculate the daily draw-down relative to the max
daily_draw_down = returns/roll_max - 1.0

# Calculate the minimum (negative) daily draw-down
max_daily_draw_down = daily_draw_down.rolling(center=False,min_periods=1,window=252).min()

# =============================================================================
# # Plot the results
# plt.figure(figsize=(15,10))
# plt.plot(returns.index, daily_draw_down, label='Daily drawdown')
# plt.plot(returns.index, max_daily_draw_down, label='Maximum daily drawdown in time-window')
# plt.legend()
# plt.show()
# 
# # Box plot
# plt.subplots()
# returns.plot(kind='box')
# plt.show()
# =============================================================================

rf = 0.001
Sharpe_Ratio = ((returns.mean() - rf) / returns.std()) * np.sqrt(252)

print("\nStock returns: " + str(round(returns.mean(), 2)))
print("Stock risk: " + str(round(returns.std(), 2)))
print('Sharpe Ratio: ' + str(round(Sharpe_Ratio, 2)))

# ### Value-at-Risk 99% Confidence
# 99% confidence interval
# 0.01 empirical quantile of daily returns
var99 = round((returns).quantile(0.01), 3)

print('\nValue at Risk (99% confidence): ' + str(var99))

# the percent value of the 5th quantile
var_1_perc = round(np.quantile(var99, 0.01), 3)
print('Percent Value-at-Risk of the 5th quantile: {:.1f}%'.format(-var_1_perc*100))

print('Value-at-Risk of 99% for 100,000 investment: ${}'.format(int(-var99 * 100000)))

# ### Value-at-Risk 95% Confidence
var95 = round((returns).quantile(0.05), 3)
print('Value at Risk (95% confidence): ' + str(var95))
print('Percent Value-at-Risk of the 5th quantile: {:.1f}%'.format(-var95*100))

# VaR for 100,000 investment
var_100k = "${}".format(int(-var95 * 100000))
print('Value-at-Risk of 99% for 100,000 investment: ${}'.format(int(-var95 * 100000)))

# =============================================================================
# mean = np.mean(returns)
# std_dev = np.std(returns)
# 
# returns.hist(bins=50, density=True, histtype='stepfilled', alpha=0.5)
# x = np.linspace(mean - 3*std_dev, mean + 3*std_dev, 100)
# plt.plot(x, norm.normpdf(x, mean, std_dev), "r")
# plt.title('Histogram of Returns')
# plt.show()
# 
# VaR_90 = norm.ppf(1-0.9, mean, std_dev)
# VaR_95 = norm.ppf(1-0.95, mean, std_dev)
# VaR_99 = norm.ppf(1-0.99, mean, std_dev)
# 
# print(tabulate([['90%', VaR_90], ['95%', VaR_95], ['99%', VaR_99]], headers=['Confidence Level', 'Value at Risk']))
# =============================================================================
