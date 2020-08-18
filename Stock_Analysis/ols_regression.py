import datetime
import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats

# BETA, ALPHA, OLS REGRESSION
stock = 'MSFT'
start_date = datetime.datetime(2014,12,28)
end_date = datetime.date.today()
df = DataReader(stock, 'yahoo', start_date, end_date)['Close']
sp_500 = DataReader('^GSPC', 'yahoo', start_date, end_date)['Close']

# joining the closing prices of the two datasets 
monthly_prices = pd.concat([df, sp_500], axis=1)
monthly_prices.columns = [stock, '^GSPC']

# calculate monthly returns
monthly_returns = monthly_prices.pct_change(1)
clean_monthly_returns = monthly_returns.dropna(axis=0)  # drop first missing row

# split dependent and independent variable
X = clean_monthly_returns['^GSPC']
y = clean_monthly_returns[stock]

# Add a constant to the independent value
X1 = sm.add_constant(X)

# make regression model 
model = sm.OLS(y, X1)

# fit model and print results
results = model.fit()
print(results.summary())

# alternatively scipy linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

plt.figure(figsize=(14,7))
X.plot()
y.plot()
plt.ylabel("Daily Returns")
fig, ax = plt.subplots()
plt.show()

# Calculate the mean of x and y
Xmean = np.mean(X)
ymean = np.mean(y)

# Calculate the terms needed for the numerator and denominator of beta
df['xycov'] = (X.dropna() - Xmean)*(y.dropna() - ymean)
df['xvar'] = (X.dropna() - Xmean)**2

#Calculate beta and alpha
beta = df['xycov'].sum()/df['xvar'].sum()
alpha = ymean-(beta*Xmean)
print(f'alpha = {alpha}')
print(f'beta = {beta}')

# Generate Line
xlst = np.linspace(np.min(X),np.max(X),100)
ylst = np.array([beta*xvl+alpha for xvl in xlst])

# Plot
plt.scatter(X, y, alpha=0.5)
plt.scatter(X, y, color='r')
plt.scatter(y, X, color='b')
plt.plot(xlst,ylst,'k-')

plt.title(f'Percentage Returns for {stock} against the S&P 500')
plt.xlabel('Company')
plt.ylabel('S&P 500')
plt.grid()
ax = plt.gca()
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_position('zero')
ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
fig, ax = plt.subplots()
plt.show()