# Import necessary libraries
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
import sys
import os

# Ensuring parent directory is in path for module import
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import tickers as ti

# Setting up date range for stock data
num_of_years = 1
start = dt.date.today() - dt.timedelta(days=int(365.25 * num_of_years))
end = dt.date.today()

# Retrieve S&P 500 tickers and adjust ticker formatting
tickers = ti.tickers_sp500()
tickers = [item.replace(".", "-") for item in tickers]

# Fetch and process stock data
dataset = pdr.get_data_yahoo(tickers, start, end)["Adj Close"]
stocks_returns = np.log(dataset / dataset.shift(1))

# Compute and print correlation matrix
corr_matrix = stocks_returns.corr()
print("\nCorrelation Matrix\n", corr_matrix)

# Function to visualize correlation matrix as a heatmap
def visualize_correlation_matrix(df_corr):
    data = df_corr.values
    plt.rcParams["figure.figsize"] = (15, 10)
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)

    # Set axis ticks and labels
    ax.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.set_xticklabels(df_corr.columns, rotation=90)
    ax.set_yticklabels(df_corr.index)

    # Setting heatmap color limits
    heatmap.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()

visualize_correlation_matrix(corr_matrix)

# Helper functions to identify top correlated stock pairs
def get_redundant_pairs(df):
    pairs_to_drop = set()
    for i in range(df.shape[1]):
        for j in range(i + 1):
            pairs_to_drop.add((df.columns[i], df.columns[j]))
    return pairs_to_drop

def get_top_abs_correlations(df, n=25):
    au_corr = df.abs().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    return au_corr[0:n]

# Displaying top absolute correlations
print("\nTop Absolute Correlations")
print(get_top_abs_correlations(stocks_returns))