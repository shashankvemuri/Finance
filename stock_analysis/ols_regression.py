import datetime
import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats

# Configure the stock symbol, start, and end dates for data
stock = 'MSFT'
start_date = datetime.datetime(2014, 12, 28)
end_date = datetime.date.today()

# Fetch stock and S&P 500 data
stock_data = DataReader(stock, 'yahoo', start_date, end_date)['Close']
sp500_data = DataReader('^GSPC', 'yahoo', start_date, end_date)['Close']

# Combine data into a single DataFrame and calculate monthly returns
combined_data = pd.concat([stock_data, sp500_data], axis=1)
combined_data.columns = [stock, 'S&P500']
monthly_returns = combined_data.pct_change().dropna()

# Define dependent and independent variables for regression
X = monthly_returns['S&P500']  # Independent variable (S&P500 returns)
y = monthly_returns[stock]  # Dependent variable (Stock returns)

# Ordinary Least Squares (OLS) Regression using statsmodels
X_sm = sm.add_constant(X)  # Adding a constant
model = sm.OLS(y, X_sm)  # Model definition
results = model.fit()  # Fit the model
print(results.summary())  # Print the results summary

# Linear Regression using scipy
slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

# Plotting stock and S&P 500 returns
plt.figure(figsize=(14, 7))
plt.scatter(X, y, alpha=0.5, label='Daily Returns')
plt.plot(X, intercept + slope * X, color='red', label='Regression Line')
plt.title(f'Regression Analysis: {stock} vs S&P 500')
plt.xlabel('S&P 500 Daily Returns')
plt.ylabel(f'{stock} Daily Returns')
plt.legend()
plt.grid(True)
plt.show()

# Calculate beta and alpha
beta = slope
alpha = intercept
print(f'alpha (intercept) = {alpha:.4f}')
print(f'beta (slope) = {beta:.4f}')