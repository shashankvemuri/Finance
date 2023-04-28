import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Set the stock symbol and time frame for the analysis
symbol = 'MSFT'
start_date = dt.date.today() - dt.timedelta(days=365)
end_date = dt.date.today()

# Set the initial investment
initial_investment = 5000

# Download data for the given stock symbol and time frame
dataset = yf.download(symbol, start_date, end_date)

# Calculate the number of shares to buy with the initial investment
shares = round(int(initial_investment / dataset['Adj Close'][0]), 1)

# Calculate the purchase price and the current value of the investment
purchase_price = dataset['Adj Close'][0]
current_value = shares * dataset['Adj Close'][-1]

# Calculate the profit or loss
profit_or_loss = current_value - initial_investment

# Calculate the percentage gain or loss
percentage_gain_or_loss = (profit_or_loss / current_value) * 100

# Calculate the percentage of returns
percentage_returns = (current_value - initial_investment) / initial_investment * 100

# Calculate the net gains or losses
net_gains_or_losses = (dataset['Adj Close'][-1] - dataset['Adj Close'][0]) / dataset['Adj Close'][0] * 100

# Calculate the total returns
total_return = ((current_value / initial_investment) - 1) * 100

# Add the calculated columns to the dataset
dataset['Shares'] = dataset['End'] = 0
dataset['Shares'] = dataset['End'].shift(1) / dataset['Adj Close'].shift(1)
dataset['PnL'] = dataset['Shares'] * (dataset['Adj Close'] - dataset['Adj Close'].shift(1))
dataset['End'] = dataset['End'].shift(1) + dataset['PnL']

# Visualize the profit and loss for each day
plt.figure(figsize=(16,8))
plt.plot(dataset['PnL'])
plt.title('Profit and Loss for Each Day')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# Print the financial analysis
print("Financial Analysis")
print('-' * 50)
print(f"{symbol} profit or loss: ${profit_or_loss:.2f}")
print(f"Percentage gain or loss: {percentage_gain_or_loss:.2f}%")
print(f"Percentage of returns: {percentage_returns:.2f}%")
print(f"Net gains or losses: {net_gains_or_losses:.2f}%")
print(f"Total Returns: {total_return:.2f}%")