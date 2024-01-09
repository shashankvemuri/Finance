import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.pylab import rcParams
from fastai.tabular.all import add_datepart
import tensorflow as tf

# Set plot size
rcParams['figure.figsize'] = 20, 10

# Download historical data for Google stock
data = yf.download('GOOGL', '2015-09-08', '2020-09-08')

# Moving Average and other calculations
data['MA50'] = data['Close'].rolling(50).mean()
data['MA200'] = data['Close'].rolling(200).mean()

# Plotting stock prices with moving averages
plt.figure(figsize=(16, 8))
plt.plot(data['Close'], label='GOOGL Close Price')
plt.plot(data['MA50'], label='50 Day MA')
plt.plot(data['MA200'], label='200 Day MA')
plt.legend()
plt.show()

# Preprocessing for Linear Regression and k-Nearest Neighbors
data.reset_index(inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data = add_datepart(data, 'Date')
data.drop('Elapsed', axis=1, inplace=True)  # Remove Elapsed column

# Scaling data
scaler = MinMaxScaler(feature_range=(0, 1))
data_scaled = scaler.fit_transform(data.drop(['Close'], axis=1))

# Train-test split
train_size = int(len(data) * 0.8)
train_data = data_scaled[:train_size]
test_data = data_scaled[train_size:]

# Separate features and target variable
X_train, y_train = train_data[:, 1:], train_data[:, 0]
X_test, y_test = test_data[:, 1:], test_data[:, 0]

# Linear Regression model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_predictions = lr_model.predict(X_test)

# k-Nearest Neighbors model
knn_model = GridSearchCV(KNeighborsRegressor(), {'n_neighbors': range(1, 10)}, cv=5)
knn_model.fit(X_train, y_train)
knn_predictions = knn_model.predict(X_test)

# TensorFlow Keras model (Multilayer Perceptron)
mlp_model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(50, activation='relu', input_dim=X_train.shape[1]),
    tf.keras.layers.Dense(50, activation='relu'),
    tf.keras.layers.Dense(1)
])
mlp_model.compile(optimizer='adam', loss='mean_squared_error')
mlp_model.fit(X_train, y_train, epochs=100)
mlp_predictions = mlp_model.predict(X_test)

# Plot predictions from each model
plt.figure(figsize=(16, 8))
plt.plot(y_test, label='Actual')
plt.plot(lr_predictions, label='Linear Regression Predictions')
plt.plot(knn_predictions, label='kNN Predictions')
plt.plot(mlp_predictions, label='MLP Predictions')
plt.legend()
plt.show()