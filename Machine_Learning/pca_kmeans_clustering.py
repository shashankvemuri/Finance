# Import necessary libraries
from pandas_datareader import DataReader 
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import numpy as np
import plotly.graph_objects as go
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# List of companies to analyze
companies = ['TGT', 'AMZN', 'NFLX', 'PG', 'NSRGY', 'MDLZ', 'MRK', 'MSFT', 'AAPL']

# Define the start and end date for data collection
start_date = datetime.datetime(2017, 5, 17)
end_date = datetime.date.today()

# Get the stock market data for the companies and filter the relevant columns
df = DataReader(companies, 'yahoo', start_date, end_date)
df = df['Open', 'Close', 'High']

# Calculate the daily movements of each stock
movements = df['Close'] - df['Open']

# Calculate the sum of movements for each stock
sum_of_movement = movements.sum(axis=1)

# Print the sum of movements for each stock
for i, company in enumerate(companies):
    print(f"Company: {company}, Change: {sum_of_movement[i]}")

# Normalize the movements data
normalizer = Normalizer()
norm_movements = normalizer.fit_transform(movements)

# Create a KMeans model
kmeans = KMeans(max_iter=1000)

# Use a pipeline to normalize and cluster the data
pipeline = make_pipeline(normalizer, kmeans)
pipeline.fit(movements)

# Get the labels of each data point
labels = pipeline.predict(movements)

# Create a dataframe of the labels and companies, sorted by labels
df_labels = pd.DataFrame({'labels': labels, 'companies': companies}).sort_values(by=['labels'], axis=0)
df_labels = df_labels.set_index('companies')
print('\n')
print(df_labels)

# Reduce the data to 2 dimensions using PCA
reduced_data = PCA(n_components=2).fit_transform(norm_movements)

# Cluster the reduced data
kmeans.fit(reduced_data)
labels = kmeans.predict(reduced_data)

# Create a dataframe of the labels and companies, sorted by labels
df_labels_reduced = pd.DataFrame({'labels': labels, 'companies': companies}).sort_values(by=['labels'], axis=0)
df_labels_reduced = df_labels_reduced.set_index('companies')
print('\n')
print(df_labels_reduced)

# Plot the clusters using the reduced data
h = 0.01
x_min, x_max = reduced_data[:,0].min() - 1, reduced_data[:,0].max() + 1
y_min, y_max = reduced_data[:,1].min() - 1, reduced_data[:,1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
cmap = plt.cm.Paired

plt.clf()
plt.figure(figsize=(10,10))
plt.imshow(Z, interpolation='nearest', extent=(xx.min(), xx.max(), yy.min(), yy.max()), cmap=cmap, aspect='auto', origin='lower')
plt.plot(reduced_data[:,0], reduced_data[:,1], 'k.', markersize=5)

# Plot the centroid of each cluster as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:,0],centroids[:,1],marker = 'x',s = 169,linewidths = 3,color = 'w',zorder = 10)
plt.title('K-Means Clustering on Stock Market Movements (PCA-Reduced Data)')
plt.xlim(x_min,x_max)
plt.ylim(y_min,y_max)
plt.show()