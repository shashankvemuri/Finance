import numpy as np
import warnings
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
from yahoo_fin import stock_info as si
import pandas as pd

warnings.filterwarnings("ignore")
yf.pdr_override()

num_of_years = 1
start = dt.date.today() - dt.timedelta(days = int(365.25*num_of_years))
end = dt.date.today()

tickers = si.tickers_nasdaq()
dataset = pdr.get_data_yahoo(tickers, start, end)['Adj Close']
dataset.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/NASDAQ_prices.csv')
# dataset = pd.read_csv('/Users/shashank/Documents/Code/Python/Research/s&p500/betaDistribution/S&P500_stock_prices.csv', index_col=0, parse_dates = True)

stocks_returns = np.log(dataset/dataset.shift(1))

print('Covariance Matrix')
cov_matrix = stocks_returns.cov()
print (cov_matrix)

print('\nCorrelation Matrix')
corr_matrix = stocks_returns.corr()
print (corr_matrix)

def get_redundant_pairs(df):
    pairs_to_drop = set()
    cols = df.columns
    for i in range(0, df.shape[1]):
        for j in range(0, i+1):
            pairs_to_drop.add((cols[i], cols[j]))
    return pairs_to_drop

def get_top_abs_correlations(df, n):
    au_corr = df.corr().abs().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    return au_corr[0:n]

print("\nTop Absolute Correlations")
print(get_top_abs_correlations(stocks_returns, 50))