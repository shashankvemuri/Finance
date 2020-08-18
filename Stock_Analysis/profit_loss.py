import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'MSFT'
start = dt.date.today() - dt.timedelta(days = 365)
end = dt.date.today()
Start = 5000 # How much to invest

# Read data 
dataset = yf.download(symbol,start,end)

# View Columns
dataset.head()
dataset.tail()

dataset['Shares'] = 0
dataset['PnL'] = 0
dataset['End'] = Start

dataset['Shares'] = dataset['End'].shift(1) / dataset['Adj Close'].shift(1)
dataset['PnL'] = dataset['Shares'] * (dataset['Adj Close'] - dataset['Adj Close'].shift(1))
dataset['End'] = dataset['End'].shift(1) + dataset['PnL']

plt.figure(figsize=(16,8))
plt.plot(dataset['PnL'])
plt.title('Profit and Loss for Daily')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# how many shares to get with the current money
Shares = round(int(float(Start) / dataset['Adj Close'][0]),1)
Purchase_Price = dataset['Adj Close'][0] # Invest in the Beginning Price
Current_Value = dataset['Adj Close'][-1] # Value of stock of Ending Price
Purchase_Cost = Shares * Purchase_Price
Current_Value = Shares * Current_Value
Profit_or_Loss = Current_Value - Purchase_Cost 

print(symbol + ' profit or loss of $%.2f' % (Profit_or_Loss))

percentage_gain_or_loss = (Profit_or_Loss/Current_Value) * 100
print('%s %%' % round(percentage_gain_or_loss,2))

percentage_returns = (Current_Value - Purchase_Cost)/ Purchase_Cost 
print('%s %%' % round(percentage_returns,2))

net_gains_or_losses = (dataset['Adj Close'][-1] - dataset['Adj Close'][0]) / dataset['Adj Close'][0]
print('%s %%' % round(net_gains_or_losses,2))


total_return = ((Current_Value/Purchase_Cost)-1) * 100
print('%s %%' % round(total_return,2))

print("Financial Analysis")
print('-' * 50)
print(symbol + ' profit or loss of $%.2f' % (Profit_or_Loss))
print('Percentage gain or loss: %s %%' % round(percentage_gain_or_loss,2))
print('Percentage of returns: %s %%' % round(percentage_returns,2))
print('Net gains or losses: %s %%' % round(net_gains_or_losses,2))
print('Total Returns: %s %%' % round(total_return,2))