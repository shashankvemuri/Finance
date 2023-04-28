# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sns
from tabulate import tabulate
import math
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta

# Get user input for the stock ticker and investment duration
symbol = input('Enter a ticker: ')
num_of_years = float(input('Enter the number of years: '))

# Calculate the start and end date for the investment period
start = dt.datetime.now() - dt.timedelta(days = int(365.25*num_of_years))
end = dt.datetime.now()

# Download the historical stock prices for the specified time period
df = yf.download(symbol,start,end)['Adj Close']

# Calculate the number of shares that can be bought with $100,000
shares = int(100000/df.iloc[0])

# Print the number of shares that can be bought, along with the beginning and current value of the investment
print('\nNumber of Shares:')
print('{}: {}'.format(symbol, shares))

print('\nBeginning Value:')
begin_value = round(shares * df.iloc[0], 2)
print('{}: ${}'.format(symbol, begin_value))

print('\nCurrent Value:')
current_value = round(shares * df.iloc[-1], 2)
print('{}: ${}'.format(symbol, current_value))

# Calculate the daily returns of the stock
returns = df.pct_change().dropna()

# Calculate the mean, standard deviation, skewness, and kurtosis of the returns
print("\nmean: " + str(round(returns.mean()*100, 2)))
print("Std. dev: " + str(round(returns.std()*100, 2)))
print("skew: " + str(round(returns.skew(), 2)))
print("kurt: " + str(round(returns.kurtosis(), 2)))

# Calculate the total return of the investment and annualize it over the investment duration
daily_cum_ret=(1+returns).cumprod()
total_return = round(daily_cum_ret.tolist()[-1], 4) * 100
print('\nTotal Return: ' + str(total_return) + '%')
annualized_return = ((1+total_return)**(1/num_of_years))-1

# Calculate the annualized volatility and sortino ratio of the investment
vol_port = returns.std() * np.sqrt(250)
target = 0
downside_returns = returns.loc[returns < target]
expected_return = returns.mean()
down_stdev = downside_returns.std()
rf = 0.01
sortino_ratio = (expected_return - rf)/down_stdev

# Print the annualized return, volatility, and sortino ratio of the investment
print('-' * 50)
print("Expected return: " + str(round(expected_return*100, 2)))
print('-' * 50)
print("Volatility: " + str(round(vol_port*100, 2)))
print('-' * 50)
print("Sortino ratio: " + str(round(sortino_ratio, 2)))
print('-' * 50)

# Calculate the maximum value of the investment over rolling 252-day periods and the daily drawdown relative to the max
roll_max = returns.rolling(center=False,min_periods=1,window=252).max()
daily_draw_down = returns/roll_max - 1.0

# Calculate the minimum (negative) daily draw-down
max_daily_draw_down = daily_draw_down.rolling(center=False,min_periods=1,window=252).min()

# Plot the results
plt.figure(figsize=(15,10))
plt.plot(returns.index, daily_draw_down, label='Daily drawdown')
plt.plot(returns.index, max_daily_draw_down, label='Maximum daily drawdown in time-window')
plt.legend()
plt.show()

# Plot box plot
plt.subplots()
returns.plot(kind='box')
plt.show()

# Sharpe Ratio
rf = 0.001
Sharpe_Ratio = ((returns.mean() - rf) / returns.std()) * np.sqrt(252)
print("\nStock returns: " + str(round(returns.mean(), 2)))
print("Stock risk: " + str(round(returns.std(), 2)))
print('Sharpe Ratio: ' + str(round(Sharpe_Ratio, 2)))

# Value-at-Risk 99% Confidence
var99 = round((returns).quantile(0.01), 3)
print('\nValue at Risk (99% confidence): ' + str(var99))

# The percent value of the 5th quantile
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

# Histogram of returns
mean = np.mean(returns)
std_dev = np.std(returns)
returns.hist(bins=50, density=True, histtype='stepfilled', alpha=0.5)
x = np.linspace(mean - 3*std_dev, mean + 3*std_dev, 100)
plt.plot(x, norm.normpdf(x, mean, std_dev), "r")
plt.title('Histogram of Returns')
plt.show()

# Confidence Level at each VaR
VaR_90 = norm.ppf(1-0.9, mean, std_dev)
VaR_95 = norm.ppf(1-0.95, mean, std_dev)
VaR_99 = norm.ppf(1-0.99, mean, std_dev)
print(tabulate([['90%', VaR_90], ['95%', VaR_95], ['99%', VaR_99]], headers=['Confidence Level', 'Value at Risk']))