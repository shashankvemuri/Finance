# Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Set stock symbol and time frame
symbol = 'BAC'
num_of_years = 1
start = dt.date.today() - dt.timedelta(days=365 * num_of_years)
end = dt.date.today()

# Download stock data using yfinance package
df = yf.download(symbol, start, end)

# Calculate daily returns
df['Returns'] = df['Adj Close'].pct_change()

# Drop rows with missing data
df.dropna(inplace=True)

# Print the first few rows of the data
print(df.head())

# Calculate the Kelly criterion
returns = np.array(df['Returns'])
wins = returns[returns > 0]
losses = returns[returns <= 0]

W = len(wins) / len(returns)
R = np.mean(wins) / np.abs(np.mean(losses))
Kelly = W - ((1 - W) / R)

# Print the result
print('Kelly Criterion: {}%'.format(np.round(Kelly, 3)))