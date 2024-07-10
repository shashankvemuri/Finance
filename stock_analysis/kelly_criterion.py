import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt

# Define stock symbol and time frame for analysis
symbol = 'BAC'
num_of_years = 1
start_date = dt.date.today() - dt.timedelta(days=365 * num_of_years)
end_date = dt.date.today()

# Download stock data using yfinance package
stock_data = yf.download(symbol, start=start_date, end=end_date)

# Calculate daily returns and drop rows with missing data
stock_data['Returns'] = stock_data['Adj Close'].pct_change()
stock_data.dropna(inplace=True)

# Display the first few rows of the data for verification
print(stock_data.head())

# Calculate Kelly Criterion
# Extract positive (wins) and negative (losses) returns
wins = stock_data['Returns'][stock_data['Returns'] > 0]
losses = stock_data['Returns'][stock_data['Returns'] <= 0]

# Calculate win ratio and win-loss ratio
win_ratio = len(wins) / len(stock_data['Returns'])
win_loss_ratio = np.mean(wins) / np.abs(np.mean(losses))

# Apply Kelly Criterion formula
kelly_criterion = win_ratio - ((1 - win_ratio) / win_loss_ratio)

# Print the Kelly Criterion percentage
print('Kelly Criterion: {:.3f}%'.format(kelly_criterion * 100))