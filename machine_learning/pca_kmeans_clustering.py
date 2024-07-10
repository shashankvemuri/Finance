# Import necessary libraries
import pandas as pd
import datetime
import numpy as np
from pandas_datareader import DataReader
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# List of companies and date range for data collection
companies = ['TGT', 'AMZN', 'NFLX', 'PG', 'NSRGY', 'MDLZ', 'MRK', 'MSFT', 'AAPL']
start_date = datetime.datetime(2017, 5, 17)
end_date = datetime.date.today()

# Fetch stock data
df = DataReader(companies, 'yahoo', start_date, end_date)['Adj Close']

# Calculate daily returns
returns = df.pct_change().dropna()

# Normalize the data
normalizer = Normalizer()
norm_movements = normalizer.fit_transform(returns)

# KMeans clustering
kmeans = KMeans(n_clusters=5)
pipeline = make_pipeline(normalizer, kmeans)
pipeline.fit(returns)
labels = pipeline.predict(returns)

# Reduce the data to 2 dimensions with PCA
pca = PCA(n_components=2)
reduced_data = pca.fit_transform(norm_movements)

# Cluster the reduced data
kmeans.fit(reduced_data)
reduced_labels = kmeans.predict(reduced_data)

# Create DataFrame for the results
df_labels = pd.DataFrame({'Label': labels, 'Company': companies}).set_index('Company')
df_reduced_labels = pd.DataFrame({'Label': reduced_labels, 'Company': companies}).set_index('Company')

# Plot the clusters with PCA-reduced data
plt.figure(figsize=(10, 10))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=reduced_labels)
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', s=100, color='red')
plt.title('K-Means Clustering on Stock Market Movements (PCA-Reduced Data)')
plt.show()

# Print clustering results
print("Clustering Results Without PCA Reduction:")
print(df_labels)
print("\nClustering Results With PCA Reduction:")
print(df_reduced_labels)