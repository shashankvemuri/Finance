# Import dependencies
import pandas as pd
from sklearn.cluster import KMeans
import pylab as pl
from math import sqrt
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import tickers as ti

# Load stock data from Dow Jones Index
yf.pdr_override()
stocks = ti.tickers_dow()
start_date = dt.datetime(2010, 1, 1)
end_date = dt.datetime.now()

# Retrieve adjusted closing prices
data = pdr.get_data_yahoo(stocks, start=start_date, end=end_date)['Close']

# Calculate annual mean returns and variances
annual_returns = data.pct_change().mean() * 252
annual_variances = data.pct_change().std() * sqrt(252)

# Combine returns and variances into a DataFrame
ret_var = pd.concat([annual_returns, annual_variances], axis=1).dropna()
ret_var.columns = ["Returns", "Variance"]

# KMeans clustering
X = ret_var.values
sse = [KMeans(n_clusters=k).fit(X).inertia_ for k in range(2, 15)]

# Plotting the elbow curve to find optimal k
pl.plot(range(2, 15), sse)
pl.title("Elbow Curve")
pl.show()

# Apply KMeans with chosen number of clusters
kmeans = KMeans(n_clusters=5).fit(X)

# Plotting the clustering result
pl.scatter(X[:, 0], X[:, 1], c=kmeans.labels_, cmap="rainbow")
pl.title("KMeans Clustering of Stocks")
pl.xlabel("Annual Return")
pl.ylabel("Annual Variance")
pl.show()

# Creating a DataFrame with tickers and their cluster labels
df = pd.DataFrame({'Stock': ret_var.index, 'Cluster': kmeans.labels_})
df.set_index('Stock', inplace=True)

print(df)