import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
from yahoo_fin import stock_info as si

plt.rcParams['figure.figsize'] = (15, 10)

tickers = si.tickers_dow()
individual_stock = input(f"Which of the following stocks would you like to backtest \n{tickers}\n:")

num_of_years = 1
start = datetime.date.today() - datetime.timedelta(days = int(365.25*num_of_years))
yf_prices = yf.download(tickers, start=start)

# Individual Stock Strategy
prices = yf_prices['Adj Close'][individual_stock]
rs = prices.apply(np.log).diff(1).fillna(0)

w1 = 5
w2 = 22
ma_x = prices.rolling(w1).mean() - prices.rolling(w2).mean()
pos = ma_x.apply(np.sign)

fig, ax = plt.subplots(2,1)
ma_x.plot(ax=ax[0], title=f'{individual_stock} Moving Average Crossovers and Positions')
pos.plot(ax=ax[1])
plt.show()

my_rs = pos.shift(1)*rs
plt.subplots()
my_rs.cumsum().apply(np.exp).plot(title=f'{individual_stock} MA Strategy Performance')
rs.cumsum().apply(np.exp).plot()
plt.legend([f'{individual_stock} MA Performace', f'{individual_stock} Buy and Hold Performnace'])
plt.show()

print (f'Performance Statistics for {individual_stock} ({num_of_years} years):')
print ('Moving Average Return: ' + str(100 * round(my_rs.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')
print('Buy and Hold Return: ' + str(100 * round(rs.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')

# Full Portfolio Strategy
prices = yf_prices['Adj Close']
rs = prices.apply(np.log).diff(1).fillna(0)

w1 = 5
w2 = 22
ma_x = prices.rolling(w1).mean() - prices.rolling(w2).mean()
pos = ma_x.apply(np.sign)
pos /= pos.abs().sum(1).values.reshape(-1,1)

fig, ax = plt.subplots(2,1)
ma_x.plot(ax=ax[0], title='Individual Moving Average Crossovers and Positions')
ax[0].legend(bbox_to_anchor=(1.1, 1.05))
pos.plot(ax=ax[1])
ax[1].legend(bbox_to_anchor=(1.1, 1.05))
plt.show()

my_rs = (pos.shift(1)*rs)
my_rs.cumsum().apply(np.exp).plot(title='Individual Stocks Strategy Performance')
plt.show()

print ('-' * 60)
print (f'Performance Statistics for {num_of_years} years:')
for i in range(len(tickers)):
    print (f'Moving Average Return for {tickers[i]}: ' + str(100 * round(my_rs.cumsum().apply(np.exp)[tickers[i]].tolist()[-1], 4)) + '%')
    i = i + 1

plt.subplots()
my_rs = (pos.shift(1)*rs).sum(1)
my_rs.cumsum().apply(np.exp).plot(title='Full Portfolio Strategy Performance')
rs.mean(1).cumsum().apply(np.exp).plot()
plt.legend(['Portfolio MA Performace', 'Buy and Hold Performnace'])
plt.show()

print ('-' * 60)
print (f'Performance Statistics for {tickers} ({num_of_years} years):')
print ('Moving Average Return: ' + str(100 * round(my_rs.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')
print('Buy and Hold Return: ' + str(100 * round(rs.mean(1).cumsum().apply(np.exp).tolist()[-1], 4)) + '%')

# Portfolio Tests
# Look-Ahead Bias
my_rs1 = (pos*rs).sum(1)
my_rs2 = (pos.shift(1)*rs).sum(1)

plt.subplots()
my_rs1.cumsum().apply(np.exp).plot(title='Full Portfolio Performance')
my_rs2.cumsum().apply(np.exp).plot()
plt.legend(['With Look-Ahead Bias', 'Without Look-Ahead Bias'])
plt.show()

print ('-' * 60)
print (f'Performance Statistics for {tickers} ({num_of_years} years):')
print ('With Look-Ahead Bias: ' + str(100 * round(my_rs1.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')
print('Without Look-Ahead Bias: ' + str(100 * round(my_rs2.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')

# Signal Lags
lags = range(1, 11)
lagged_rs = pd.Series(dtype=float, index=lags)

print ('-' * 60)
print (f'Lag Performance Statistics for {tickers} ({num_of_years} years):')
for lag in lags:
    my_rs = (pos.shift(lag)*rs).sum(1)
    my_rs.cumsum().apply(np.exp).plot()
    lagged_rs[lag] = my_rs.sum()
    print (f'Lag {lag} Return: ' + str(100 * round(my_rs.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')

plt.title('Full Portfolio Strategy Performance with Lags')    
plt.legend(lags, bbox_to_anchor=(1.1, 0.95))
plt.show()

# Transaction Costs
tc_pct = 0.01

delta_pos = pos.diff(1).abs().sum(1)
my_tcs = tc_pct*delta_pos

my_rs1 = (pos.shift(1)*rs).sum(1)
my_rs2 = (pos.shift(1)*rs).sum(1) - my_tcs

plt.subplots()
my_rs1.cumsum().apply(np.exp).plot()
my_rs2.cumsum().apply(np.exp).plot()
plt.title('Full Portfolio Performance')
plt.legend(['Without Transaction Costs', 'With Transaction Costs'])
plt.show()

print ('-' * 60)
print (f'Performance Statistics for {tickers} ({num_of_years} years):')
print ('Without Transaction Costs: ' + str(100 * round(my_rs1.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')
print('With Transaction Costs: ' + str(100 * round(my_rs2.cumsum().apply(np.exp).tolist()[-1], 4)) + '%')