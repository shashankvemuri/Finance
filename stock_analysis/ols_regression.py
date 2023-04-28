# Import dependencies
import datetime
import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats

# Set variables
stock = 'MSFT'
start_date = datetime.datetime(2014, 12, 28)
end_date = datetime.date.today()

# Fetch data from Yahoo Finance
df = DataReader(stock, 'yahoo', start_date, end_date)['Close']
sp_500 = DataReader('^GSPC', 'yahoo', start_date, end_date)['Close']

# Joining the closing prices of the two datasets 
monthly_prices = pd.concat([df, sp_500], axis=1)
monthly_prices.columns = [stock, '^GSPC']

# Calculate monthly returns
monthly_returns = monthly_prices.pct_change(1)
clean_monthly_returns = monthly_returns.dropna(axis=0)  # drop first missing row

# Split dependent and independent variable
X = clean_monthly_returns['^GSPC'] # independent variable
y = clean_monthly_returns[stock] # dependent variable

# Add a constant to the independent value for the OLS model
X1 = sm.add_constant(X)

# Make regression model using OLS
model = sm.OLS(y, X1)

# Fit model and print results summary
results = model.fit()
print(results.summary())

# Alternatively scipy linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

# Plot stock and S&P 500 daily returns
plt.figure(figsize=(14,7))
X.plot()
y.plot()
plt.ylabel("Daily Returns")
plt.show()

# Calculate the mean of X and y
Xmean = np.mean(X)
ymean = np.mean(y)

# Calculate the terms needed for the numerator and denominator of beta
df['xycov'] = (X.dropna() - Xmean) * (y.dropna() - ymean)
df['xvar'] = (X.dropna() - Xmean) ** 2

# Calculate beta and alpha
beta = df['xycov'].sum() / df['xvar'].sum()
alpha = ymean - (beta * Xmean)
print(f'alpha = {alpha}')
print(f'beta = {beta}')

# Generate line for plot
xlst = np.linspace(np.min(X), np.max(X), 100)
ylst = np.array([beta * xvl + alpha for xvl in xlst])

# Plot stock and S&P 500 daily returns with regression line
plt.scatter(X, y, alpha=0.5)
plt.scatter(X, y, color='r')
plt.scatter(y, X, color='b')
plt.plot(xlst, ylst, 'k-')

plt.title(f'Percentage Returns for {stock} against the S&P 500')
plt.xlabel('Company')
plt.ylabel('S&P 500')
plt.grid()
ax = plt.gca()
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_position('zero')
ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
plt.show()