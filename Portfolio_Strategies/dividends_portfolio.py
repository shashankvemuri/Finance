# # Stocks Dividends Portfolio

# ## Stocks with Dividend

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yfd
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta


# input
symbols = ['ALX','BLK','SPG','LMT']
start = dt.datetime.now() - dt.timedelta(days = 365*12)
end = dt.datetime.now()

# Read data 
df = yf.download(symbols,start,end)['Adj Close']

delta = relativedelta.relativedelta(start,end)
print('How many years of investing?')
print('%s years' % delta.years)

for s in symbols: 
    df[s].plot(label = s, figsize = (15,10))
plt.legend()

for s in symbols:
    print(s + ":",  df[s].max())

for s in symbols:
    print(s + ":",  df[s].min())

returns = pd.DataFrame()
for s in symbols: 
    returns[s + " Return"] = (np.log(1 + df[s].pct_change())).dropna()
    
sns.pairplot(returns[1:])
plt.show()

# dates each bank stock had the best and worst single day returns. 
print('Best Day Returns')
print('-'*20)
print(returns.idxmax())
print('\n')
print('Worst Day Returns')
print('-'*20)
print(returns.idxmin())

plt.figure(figsize=(14,7))

for r in returns:
    sns.kdeplot(returns.ix["2011-01-01" : "2011-12-31 "][r])

print(returns.corr())

# Heatmap for return of all the banks
plt.figure(figsize=(14,7))
sns.heatmap(returns.corr(), cmap="cool",linewidths=.1, annot= True)
sns.clustermap(returns.corr(), cmap="Wistia",linewidths=.1, annot= True)
plt.show()

plt.figure(figsize=(14,7))
sns.heatmap(df.corr(), cmap="hot",linewidths=.1, annot= True)
sns.clustermap(df.corr(), cmap="copper",linewidths=.1, annot= True)
plt.show()

Cash = 100000
print('Percentage of invest:')
percent_invest = [0.25, 0.25, 0.25, 0.25]
for i, x in zip(df.columns, percent_invest):
    cost = x * Cash
    print('{}: {}'.format(i, cost))

print('Number of Shares:')
percent_invest = [0.25, 0.25, 0.25, 0.25]
for i, x, y in zip(df.columns, percent_invest, df.iloc[0]):
    cost = x * Cash
    shares = int(cost/y)
    print('{}: {}'.format(i, shares))

print('Beginning Value:')
percent_invest = [0.25, 0.25, 0.25, 0.25]
for i, x, y in zip(df.columns, percent_invest, df.iloc[0]):
    cost = x * Cash
    shares = int(cost/y)
    Begin_Value = round(shares * y, 2)
    print('{}: ${}'.format(i, Begin_Value))

print('Current Value:')
percent_invest = [0.25, 0.25, 0.25, 0.25]
for i, x, y, z in zip(df.columns, percent_invest, df.iloc[0], df.iloc[-1]):
    cost = x * Cash
    shares = int(cost/y)
    Current_Value = round(shares * z, 2)
    print('{}: ${}'.format(i, Current_Value))

result = []
percent_invest = [0.25, 0.25, 0.25, 0.25]
for i, x, y, z in zip(df.columns, percent_invest, df.iloc[0], df.iloc[-1]):
    cost = x * Cash
    shares = int(cost/y)
    Current_Value = round(shares * z, 2)
    result.append(Current_Value)
print('Total Value: $%s' % round(sum(result),2))

stock = yfd.Tickers('ALX BLK SPG LMT')
s1_dividend = stock.ALX.dividends[str(start):].sum()
s2_dividend = stock.BLK.dividends[str(start):].sum()
s3_dividend = stock.SPG.dividends[str(start):].sum()
s4_dividend = stock.LMT.dividends[str(start):].sum()

data = [s1_dividend, s2_dividend, s3_dividend, s4_dividend]

print('Total Dividends:')
data = [s1_dividend, s2_dividend, s3_dividend, s4_dividend]
for i, x in zip(df.columns, data):
    print('{}: {}'.format(i, x))

print('Dividends with Shares:')
percent_invest = [0.25, 0.25, 0.25, 0.25]
data = [s1_dividend, s2_dividend, s3_dividend, s4_dividend]
for i, x, y in zip(df.columns, percent_invest, data):
    cost = x * Cash
    shares = int(cost/y)
    total_dividend_cost = shares * y
    print('{}: ${}'.format(i, round(total_dividend_cost,2)))

dividend = []
percent_invest = [0.25, 0.25, 0.25, 0.25]
data = [s1_dividend, s2_dividend, s3_dividend, s4_dividend]
for i, x, y in zip(df.columns, percent_invest, data):
    cost = x * Cash
    shares = int(cost/y)
    total_dividend_cost = shares * y
    dividend.append(total_dividend_cost)
print('Total Dividends: $%s' % round(sum(dividend),2))

print('Total Money: $%s' % round((sum(dividend) + sum(result)),2))
print('Total Profit: $%s' % (round((sum(dividend) + sum(result)),2) - Cash))