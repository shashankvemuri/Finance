import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import datetime
from pandas_datareader import data as pdr

yf.pdr_override()

num_of_years = .5
start = datetime.date.today() - datetime.timedelta(days = int(365.25 * num_of_years))
end = datetime.date.today()


stocks = ['CFG', 'KEY', 'JPM', 'SPY']
data = pdr.get_data_yahoo(stocks, start, end)['Adj Close']
data = data.dropna()

def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.01:
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs

scores, pvalues, pairs = find_cointegrated_pairs(data)
seaborn.heatmap(pvalues, xticklabels = data.columns, yticklabels = data.columns, cmap = 'plasma', mask = (pvalues >= 0.01))
plt.rcParams['figure.figsize'] = (15, 10)
plt.title('Heatmap of Co-Integrated Stocks')
plt.subplots()
plt.show()

#normalize stock prices
def zscore(stocks):
    return (stocks - stocks.mean())/np.std(stocks)

if len(pairs) == 0:
    print ('There were no pairs in the inputted list!')

else:
    coint_pairs = pairs
    values = []
    
    n = 0
    for i in coint_pairs:
        S1 = data[i[0]]
        S2 = data[i[1]]
        score, pvalue, _ = coint(S1, S2)
        print(f'p-value between {i[0]} and {i[1]}: ' + str(pvalue))
        values.append(pvalue)
    
    min_val = np.argmin(values)
    spread = data[pairs[min_val][0]] - data[pairs[min_val][1]]
    
    spread_mavg1 = spread.rolling(1).mean()
    spread_mavg20 = spread.rolling(20).mean()
    spread_std20 = spread.rolling(20).std()
    zscore_20_1 = (spread_mavg1 - spread_mavg20)/spread_std20
    plt.rcParams['figure.figsize'] = (15, 10)
    zscore_20_1.plot(label = 'Rolling 20 day z score')
    plt.axhline(0,color = 'black')
    plt.axhline(1, c ='r',ls='--')
    plt.axhline(-1, c ='r',ls='--')
    plt.title(f'Rolling 20-Day Spread Between {pairs[min_val][0]} and {pairs[min_val][1]}')
    plt.xlabel('Dates')
    plt.ylabel('Spread')
    plt.show()