import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta

# input
# Machine Learning Stock
symbols = ['GOOGL','MSFT','FB','AMZN','NFLX','CRM','ADBE','MTCH','IAC','TTD','FIVN','V','MA','PANW','IBM','FTNT','NVDA','INTC','CUB','IBM','ACN','EPAM']
start = dt.datetime.now() - dt.timedelta(days = 365*2)
end = dt.datetime.now()

df = pd.DataFrame()
for s in symbols:
    df[s] = yf.download(s,start,end)['Adj Close']

delta = relativedelta.relativedelta(start,end)
print('How many years of investing?')
print('%s years' % delta.years)

number_of_years = delta.years

days = (df.index[-1] - df.index[0]).days

plt.figure(figsize=(14,7))
plt.plot(df)
plt.title('Machine Learning Stocks Closing Price')
plt.legend(labels=df.columns)
plt.show()

# Normalize the data
normalize = (df - df.min())/ (df.max() - df.min())

plt.figure(figsize=(18,12))
plt.plot(normalize)
plt.title('Machine Learning Stocks Normalize')
plt.legend(labels=normalize.columns)
plt.show()

stock_rets = df.pct_change().dropna()

plt.figure(figsize=(14,7))
plt.plot(stock_rets)
plt.title('Machine Learning Stocks Returns')
plt.legend(labels=stock_rets.columns)
plt.show()

plt.figure(figsize=(14,7))
plt.plot(stock_rets.cumsum())
plt.title('Machine Learning Stocks Returns Cumulative Sum')
plt.legend(labels=stock_rets.columns)
plt.show()

sns.set(style='ticks')
ax = sns.pairplot(stock_rets, diag_kind='hist')
plt.show()

nplot = len(stock_rets.columns)
for i in range(nplot) :
    for j in range(nplot) :
        ax.axes[i, j].locator_params(axis='x', nbins=6, tight=True)

ax = sns.PairGrid(stock_rets)
ax.map_upper(plt.scatter, color='purple')
ax.map_lower(sns.kdeplot, color='blue')
ax.map_diag(plt.hist, bins=30)
for i in range(nplot) :
    for j in range(nplot) :
        ax.axes[i, j].locator_params(axis='x', nbins=6, tight=True)

plt.figure(figsize=(7,7))
corr = stock_rets.corr()

# plot the heatmap
sns.heatmap(corr, 
        xticklabels=corr.columns,
        yticklabels=corr.columns,
            cmap="Blues")

# Box plot
stock_rets.plot(kind='box',figsize=(12,8))
rets = stock_rets.dropna()
plt.figure(figsize=(14,7))
plt.scatter(rets.mean(), rets.std(),alpha = 0.5)
plt.title('Stocks Risk & Returns')
plt.xlabel('Expected returns')
plt.ylabel('Risk')
plt.grid(which='major')
plt.show()

for label, x, y in zip(rets.columns, rets.mean(), rets.std()):
    plt.annotate(
        label, 
        xy = (x, y), xytext = (50, 50),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        arrowprops = dict(arrowstyle = '-', connectionstyle = 'arc3,rad=-0.3'))

rets = stock_rets.dropna()
area = np.pi*20.0

sns.set(style='darkgrid')
plt.figure(figsize=(14,7))
plt.scatter(rets.mean(), rets.std(), s=area)
plt.xlabel("Expected Return", fontsize=15)
plt.ylabel("Risk", fontsize=15)
plt.title("Return vs. Risk for Stocks", fontsize=20)
plt.show()

for label, x, y in zip(rets.columns, rets.mean(), rets.std()) : 
    plt.annotate(label, xy=(x,y), xytext=(50, 0), textcoords='offset points',
                arrowprops=dict(arrowstyle='-', connectionstyle='bar,angle=180,fraction=-0.2'),
                bbox=dict(boxstyle="round", fc="w"))

rest_rets = rets.corr()
pair_value = rest_rets.abs().unstack()
pair_value.sort_values(ascending = False)

# Normalized Returns Data
Normalized_Value = ((rets[:] - rets[:].min()) /(rets[:].max() - rets[:].min()))

print(Normalized_Value.corr())

normalized_rets = Normalized_Value.corr()
normalized_pair_value = normalized_rets.abs().unstack()
normalized_pair_value.sort_values(ascending = False)

print("Stock returns: ")
print(rets.mean())
print('-' * 50)
print("Stock risks:")
print(rets.std())

table = pd.DataFrame()
table['Returns'] = rets.mean()
table['Risk'] = rets.std()
table.sort_values(by='Returns')
table.sort_values(by='Risk')
rf = 0.01
table['Sharpe Ratio'] = (table['Returns'] - rf) / table['Risk']
table['Max Returns'] = rets.max()
table['Min Returns'] = rets.min()
table['Median Returns'] = rets.median()
total_return = stock_rets[-1:].transpose()
table['Total Return'] = 100 * total_return
table['Average Return Yearly'] = (1 + total_return)**(1 / number_of_years) - 1
initial_value = df.iloc[0]
ending_value = df.iloc[-1]
table['CAGR'] = ((ending_value / initial_value) ** (252.0 / days)) -1
table.sort_values(by='Average Return Yearly')
print(table)