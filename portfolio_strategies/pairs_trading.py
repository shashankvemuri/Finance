import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from statsmodels.tsa.stattools import coint
import datetime
from pandas_datareader import data as pdr
import seaborn as sns

# Override pandas_datareader's DataReader method to use Yahoo Finance
yf.pdr_override()

def download_stock_data(symbols, start_date, end_date):
    """Download historical stock data for given symbols from Yahoo Finance."""
    stock_data = pdr.get_data_yahoo(symbols, start_date, end_date)['Adj Close']
    return stock_data.dropna()

def find_cointegrated_pairs(data):
    """Identify cointegrated pairs of stocks."""
    n = data.shape[1]
    score_matrix, pvalue_matrix = np.zeros((n, n)), np.ones((n, n))
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1, S2 = data[data.columns[i]], data[data.columns[j]]
            _, pvalue, _ = coint(S1, S2)
            score_matrix[i, j], pvalue_matrix[i, j] = _, pvalue
            if pvalue < 0.05:  # Using a p-value threshold of 0.05
                pairs.append((data.columns[i], data.columns[j]))
    return score_matrix, pvalue_matrix, pairs

def plot_cointegration_heatmap(pvalues, tickers):
    """Plot heatmap of p-values for cointegration test."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(pvalues, xticklabels=tickers, yticklabels=tickers, cmap='coolwarm', mask=(pvalues >= 0.05))
    plt.title("P-Values for Pairs Cointegration Test")
    plt.show()

def main():
    # Set time period and stock tickers
    num_of_years = 5
    start = datetime.datetime.now() - datetime.timedelta(days=365 * num_of_years)
    end = datetime.datetime.now()
    stocks = ['AAPL', 'MSFT', 'GOOG', 'AMZN']

    # Download and process data
    data = download_stock_data(stocks, start, end)

    # Find cointegrated pairs
    _, pvalues, pairs = find_cointegrated_pairs(data)

    # Plot heatmap of p-values
    plot_cointegration_heatmap(pvalues, stocks)

    # Display the found pairs
    print("Cointegrated Pairs:", pairs)

if __name__ == "__main__":
    main()