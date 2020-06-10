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
symbols = ['AAPL','MSFT','AMD','NVDA']
start = dt.datetime.now() - dt.timedelta(days = 365*7)
end = dt.datetime.now()

df = pd.DataFrame()
for s in symbols:
    df[s] = yf.download(s,start,end)['Adj Close']

stock_rets = df.pct_change().dropna()

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
plt.show()

# Box plot
stock_rets.plot(kind='box')
rets = stock_rets.dropna()
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
print(normalized_pair_value.sort_values(ascending = False))

print("Stock returns: ")
print(rets.mean())
print('-' * 50)
print("Stock risks:")
print(rets.std())

table = pd.DataFrame()
table['Returns'] = rets.mean()
table['Risk'] = rets.std()
print(table.sort_values(by='Returns'))
print(table.sort_values(by='Risk'))
rf = 0.01
table['Sharpe_Ratio'] = (table['Returns'] - rf) / table['Risk']
print(table)