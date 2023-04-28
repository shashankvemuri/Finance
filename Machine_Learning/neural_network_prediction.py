# Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler

# Download stock data for Apple from Yahoo Finance API
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days=394)
end = dt.date.today()
df = yf.download(symbol,start,end)

# Calculate additional features from stock data
df['Open_Close'] = (df['Open'] - df['Adj Close']) / df['Open']
df['High_Low'] = (df['High'] - df['Low']) / df['Low']
df['Increase_Decrease'] = np.where(df['Volume'].shift(-1) > df['Volume'], 1, 0)
df['Buy_Sell_on_Open'] = np.where(df['Open'].shift(-1) > df['Open'], 1, 0)
df['Buy_Sell'] = np.where(df['Adj Close'].shift(-1) > df['Adj Close'], 1, 0)
df['Returns'] = df['Adj Close'].pct_change()
df = df.dropna()

# Define a simple neural network model using Keras
model = tf.keras.Sequential([keras.layers.Dense(units=1, input_shape=[1])])
model.compile(optimizer='sgd', loss='mean_squared_error')

# Train the model using stock returns as input and adjusted closing price as target
X = np.array(df['Returns'], dtype=float)
Y = np.array(df['Adj Close'], dtype=float)
model.fit(X, Y, epochs=100)

# Normalize the input and target variables using MinMaxScaler
scaler = MinMaxScaler()
normalized_X = scaler.fit_transform(np.array(df['Returns']).reshape(-1, 1))
X = np.array(normalized_X, dtype=float)
normalized_Y = scaler.fit_transform(np.array(df['Adj Close']).reshape(-1, 1))
Y = np.array(normalized_Y, dtype=float)

# Define a more complex neural network model using Keras
def build_model():
    model = keras.Sequential([
        layers.Dense(64, activation=tf.nn.relu, input_shape=[len(df.keys())-1]),
        layers.Dense(64, activation=tf.nn.relu),
        layers.Dense(1)])

    optimizer = tf.keras.optimizers.RMSprop(0.001)
    model.compile(loss='mean_squared_error',
                optimizer=optimizer,
                metrics=['mean_absolute_error', 'mean_squared_error'])
    return model

# Print the predicted stock price based on the model's output
print('Predicted Price: ' + str(scaler.inverse_transform(model.predict([[0]]))[0][0]))