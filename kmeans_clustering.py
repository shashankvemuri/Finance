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

#Loading the data
yf.pdr_override()
stocks = si.tickers_dow()
stocks = stocks[10:30]
start = dt.datetime(2010, 1, 1)
now = dt.datetime.now()

data = pdr.get_data_yahoo(stocks, start, now)['Close']

#Calculating annual mean returns and variances
returns = data.pct_change().mean() * 252
variance = data.pct_change().std() * sqrt(252)
returns.columns = ["Returns"]
variance.columns = ["Variance"]

#Concatenating the returns and variances into a single data-frame
ret_var = pd.concat([returns, variance], axis = 1).dropna()
ret_var.columns = ["Returns", "Variance"]

X =  ret_var.values #Converting ret_var into nummpy array
sse = []

for k in range(2,15):
    
    kmeans = KMeans(n_clusters = k)
    kmeans.fit(X)
    
    sse.append(kmeans.inertia_) #SSE for each n_clusters
pl.plot(range(2,15), sse)
pl.title("Elbow Curve")
pl.subplots()
pl.show()

kmeans = KMeans(n_clusters = 5).fit(X)
centroids = kmeans.cluster_centers_
pl.scatter(X[:,0],X[:,1], c = kmeans.labels_, cmap ="rainbow")
pl.show()

#print(returns.idxmax())
#ret_var.drop("AAPL", inplace =True)

X = ret_var.values
kmeans =KMeans(n_clusters = 5).fit(X)
centroids = kmeans.cluster_centers_
pl.scatter(X[:,0],X[:,1], c = kmeans.labels_, cmap ="rainbow")
pl.show()

Company = pd.DataFrame(ret_var.index)
cluster_labels = pd.DataFrame(kmeans.labels_)
df = pd.concat([Company, cluster_labels],axis = 1)
df.columns = ['Stock', 'Value']
df.set_index('Stock')

print (df)