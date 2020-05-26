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

companies = ['TGT', 'AMZN', 'NFLX', 'PG', 'NSRGY', 'MDLZ', 'MRK', 'MSFT', 'AAPL']

start_date = datetime.datetime(2017, 5, 17)
end_date = datetime.date.today()

df = DataReader(companies, 'yahoo', start_date, end_date)

stock_open = np.array(df['Open']).transpose()
stock_close = np.array(df['Close']).transpose()

movements = stock_close - stock_open

sum_of_movement = np.sum(movements,1)

for i in range(len(companies)):
    print('company:{}, Change:{}'.format(df['High'].columns[i],sum_of_movement[i]))

# Define, Fit, and transform a Normalizer
normalizer = Normalizer()
norm_movements = normalizer.fit_transform(movements) 

# Create Kmeans model
normalizer = Normalizer()
kmeans = KMeans(max_iter = 1000)
pipeline = make_pipeline(normalizer,kmeans)
pipeline.fit(movements)
labels = pipeline.predict(movements)

df1 = pd.DataFrame({'labels':labels,'companies':companies}).sort_values(by=['labels'],axis = 0)
df1 = df1.set_index('companies')
print('\n')
print(df1)

# Reduce the data
normalizer = Normalizer()
reduced_data = PCA(n_components = 2)
kmeans = KMeans(max_iter = 1000)
pipeline = make_pipeline(normalizer,reduced_data,kmeans)
pipeline.fit(movements)
labels = pipeline.predict(movements)

df2 = pd.DataFrame({'labels':labels,'companies':companies}).sort_values(by=['labels'],axis = 0)
df2 = df2.set_index('companies')
print('\n')
print(df2)

# Reduce the data
reduced_data = PCA(n_components = 2).fit_transform(norm_movements)
h = 0.01
x_min,x_max = reduced_data[:,0].min()-1, reduced_data[:,0].max() + 1
y_min,y_max = reduced_data[:,1].min()-1, reduced_data[:,1].max() + 1
xx,yy = np.meshgrid(np.arange(x_min,x_max,h),np.arange(y_min,y_max,h))
Z = kmeans.predict(np.c_[xx.ravel(),yy.ravel()])
Z = Z.reshape(xx.shape)
cmap = plt.cm.Paired

plt.clf()
plt.figure(figsize=(10,10))
plt.imshow(Z,interpolation = 'nearest',extent=(xx.min(),xx.max(),yy.min(),yy.max()),cmap = cmap,aspect = 'auto',origin = 'lower')
plt.plot(reduced_data[:,0],reduced_data[:,1],'k.',markersize = 5)

# Plot the centroid of each cluster as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:,0],centroids[:,1],marker = 'x',s = 169,linewidths = 3,color = 'w',zorder = 10)
plt.title('K-Means Clustering on Stock Market Movements (PCA-Reduced Data)')
plt.xlim(x_min,x_max)
plt.ylim(y_min,y_max)
plt.show()
