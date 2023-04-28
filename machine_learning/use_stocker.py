from stocker import Stocker
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20, 10
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from fastai.structured import add_datepart
import tensorflow as tf
from tensorflow.keras import layers
from sklearn import neighbors
from sklearn.model_selection import GridSearchCV
from pandas.util.testing import assert_frame_equal

goog = Stocker('GOOGL')
goog.plot_stock()

# Create model
model, model_data = goog.create_prophet_model(days=90)
goog.evaluate_prediction()

# Optimize the model
goog.changepoint_prior_analysis(changepoint_priors=[0.001, 0.05, 0.1, 0.2])
goog.changepoint_prior_validation(start_date='2016-01-04', end_date='2017-01-03', changepoint_priors=[0.001, 0.05, 0.1, 0.2])

# Evaluate the new model
goog.evaluate_prediction()
print(goog.evaluate_prediction(nshares=1000))

# Getting the dataframe of the data
goog_data = goog.make_df('2004-08-19', '2018-03-27')
print(goog_data.head(50))

goog_data = goog_data[['Date', 'Open', 'High', 'Low', 'Close', 'Adj. Close', 'Volume']]
print(goog_data.head(50))

# Moving Average
scaler = MinMaxScaler(feature_range=(0, 1))
df = goog_data
print(df.head())

df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')
df.index = df['Date']
print(df.head(50))

plt.figure(figsize=(16,8))
plt.plot(df['Date'], df['Adj. Close'], label='Close Price history')

# Creating dataframe with date and the target variable
data = df.sort_index(ascending=True, axis=0)
new_data = pd.DataFrame(index=range(0, len(df)), columns=['Date', 'Adj. Close'])

for i in range(0, len(data)):
  new_data['Date'][i] = data['Date'][i]
  new_data['Adj. Close'][i] = data['Adj. Close'][i]

# Train-test split
train = new_data[:2600]
test = new_data[2600:]

new_data.shape, train.shape, test.shape
num = test.shape[0]

train['Date'].min(), train['Date'].max(), test['Date'].min(), test['Date'].max()

# Making predictions
preds = []
for i in range(0, num):
  a = train['Adj. Close'][len(train)-924+i:].sum() + sum(preds)
  b = a/num
  preds.append(b)

len(preds)

# Measure accuracy with rmse (Root Mean Squared Error)
rms=np.sqrt(np.mean(np.power((np.array(test['Adj. Close'])-preds),2)))
print(rms)

test['Predictions'] = 0
test['Predictions'] = preds
plt.plot(train['Adj. Close'])
plt.plot(test[['Adj. Close', 'Predictions']])

# Simple Linear Regression
lr_data = goog_data
lr_data.head(50)

lr_data['Date'] = pd.to_datetime(lr_data.Date, format='%Y-%m-%d')
lr_data.index = lr_data['Date']

lr_data = lr_data.sort_index(ascending=True, axis=0)

new_data = pd.DataFrame(index=range(0, len(lr_data)), columns=['Date', 'Adj. Close'])
for i in range(0,len(data)):
    new_data['Date'][i] = lr_data['Date'][i]
    new_data['Adj. Close'][i] = lr_data['Adj. Close'][i]

print(new_data.head(50))

add_datepart(new_data, 'Date')
new_data.drop('Elapsed', axis=1, inplace=True)

# Train-test split
train = new_data[:2600]
test = new_data[2600:]

x_train = train.drop('Adj. Close', axis=1)
y_train = train['Adj. Close']
x_test = test.drop('Adj. Close', axis=1)
y_test = test['Adj. Close']

# Implementing linear regression
model = LinearRegression()
model.fit(x_train, y_train)

# Predictions 
preds = model.predict(x_test)
lr_rms = np.sqrt(np.mean(np.power((np.array(y_test)-np.array(preds)),2)))
print(lr_rms)

# Plot
test['Predictions'] = 0
test['Predictions'] = preds

plt.plot(train['Adj. Close'])
plt.plot(test[['Adj. Close', 'Predictions']])

# k-Nearest Neighbours
scaler = MinMaxScaler(feature_range=(0, 1))

# scaling the data
x_train_scaled = scaler.fit_transform(x_train)
x_train = pd.DataFrame(x_train_scaled)
x_test_scaled = scaler.fit_transform(x_test)
x_test = pd.DataFrame(x_test_scaled)

# using gridsearch to find the best value of k
params = {'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}
knn = neighbors.KNeighborsRegressor()
model = GridSearchCV(knn, params, cv=5)

# fitting the model and predicting
model.fit(x_train, y_train)
new_preds = model.predict(x_test)

# Results
k_rms = np.sqrt(np.mean(np.power((np.array(y_test)-np.array(preds)),2)))
print(k_rms)

test['Predictions'] = 0
test['Predictions'] = new_preds

plt.plot(train['Adj. Close'])
plt.plot(test[['Adj. Close', 'Predictions']])

# Multilayer Perceptron
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(100, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(100, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(1, activation=tf.nn.relu))
model.compile(optimizer='adam', loss='mean_squared_error')

X_train = np.array(x_train)
Y_train = np.array(y_train)

model.fit(X_train, Y_train, epochs=500)
preds = model.predict(x_test)

# Results
mlp_rms = np.sqrt(np.mean(np.power((np.array(y_test)-np.array(preds)),2)))
print(mlp_rms)

test['Predictions'] = 0
test['Predictions'] = preds

plt.plot(train['Adj. Close'])
plt.plot(test[['Adj. Close', 'Predictions']])