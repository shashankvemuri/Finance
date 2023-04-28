# Import dependencies
import pandas as pd
from sklearn.cluster import KMeans
from math import sqrt
import  pylab as pl
import numpy as np
import yfinance as yf
import datetime as dt
import requests
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si 

# Loading the data
yf.pdr_override()
stocks = si.tickers_dow()[10:30]  # Shorten the code for readability
start = dt.datetime(2010, 1, 1)
now = dt.datetime.now()

data = pdr.get_data_yahoo(stocks, start, now)['Close']

# Calculating annual mean returns and variances
returns = data.pct_change().mean() * 252
variance = data.pct_change().std() * sqrt(252)

# Renaming the columns
returns.name = "Returns"
variance.name = "Variance"

# Concatenating the returns and variances into a single data-frame
ret_var = pd.concat([returns, variance], axis=1).dropna()
ret_var.columns = ["Returns", "Variance"]

X = ret_var.values  # Converting ret_var into a numpy array
sse = []

for k in range(2, 15):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(X)
    sse.append(kmeans.inertia_)  # SSE for each n_clusters
    
# Plotting the elbow curve
pl.plot(range(2, 15), sse)
pl.title("Elbow Curve")
pl.show()

# Plotting the clustering result
kmeans = KMeans(n_clusters=5).fit(X)
centroids = kmeans.cluster_centers_
pl.scatter(X[:, 0], X[:, 1], c=kmeans.labels_, cmap="rainbow")
pl.show()

# Dropping the row with maximum return value
ret_var.drop(returns.idxmax(), inplace=True)

X = ret_var.values
kmeans = KMeans(n_clusters=5).fit(X)
centroids = kmeans.cluster_centers_

# Plotting the clustering result
pl.scatter(X[:, 0], X[:, 1], c=kmeans.labels_, cmap="rainbow")
pl.show()

# Creating a new data frame with stock tickers and their assigned clusters
company = pd.DataFrame(ret_var.index)
cluster_labels = pd.DataFrame(kmeans.labels_)
df = pd.concat([company, cluster_labels], axis=1)
df.columns = ['Stock', 'Cluster']
df.set_index('Stock', inplace=True)

print(df)