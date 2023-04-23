# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
import yfinance as yf

# Set up date range and get stock tickers
num_of_years = 1
start = dt.date.today() - dt.timedelta(days=int(365.25 * num_of_years))
end = dt.date.today()
tickers = si.tickers_dow()
tickers = [item.replace(".", "-") for item in tickers]

# Get daily adjusted close prices for all tickers
dataset = pdr.get_data_yahoo(tickers, start, end)["Adj Close"]
stocks_returns = np.log(dataset / dataset.shift(1))

# Compute correlation matrix and display it
print("\nCorrelation Matrix")
corr_matrix = stocks_returns.corr()
print(corr_matrix)

# Visualize correlation matrix as heatmap
def visualize_correlation_matrix(df_corr):
    data1 = df_corr.values
    plt.rcParams["figure.figsize"] = (15, 10)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()

visualize_correlation_matrix(corr_matrix)

# Define helper functions for finding top correlated pairs
def get_redundant_pairs(df):
    pairs_to_drop = set()
    cols = df.columns
    for i in range(0, df.shape[1]):
        for j in range(0, i + 1):
            pairs_to_drop.add((cols[i], cols[j]))
    return pairs_to_drop

def get_top_abs_correlations(df, n=25):
    au_corr = df.corr().abs().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    return au_corr[0:n]

# Display top absolute correlations
print("\nTop Absolute Correlations")
print(get_top_abs_correlations(stocks_returns)) 