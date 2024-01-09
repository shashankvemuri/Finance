# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt
import tensorflow as tf
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler

# Download and prepare stock data
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days=394)
end = dt.date.today()
df = yf.download(symbol, start, end)
df['Open_Close'] = (df['Open'] - df['Adj Close']) / df['Open']
df['High_Low'] = (df['High'] - df['Low']) / df['Low']
df['Increase_Decrease'] = np.where(df['Volume'].shift(-1) > df['Volume'], 1, 0)
df['Buy_Sell_on_Open'] = np.where(df['Open'].shift(-1) > df['Open'], 1, 0)
df['Buy_Sell'] = np.where(df['Adj Close'].shift(-1) > df['Adj Close'], 1, 0)
df['Returns'] = df['Adj Close'].pct_change()
df = df.dropna()

# Normalize data
scaler = MinMaxScaler()
X = scaler.fit_transform(df[['Returns']])
Y = scaler.fit_transform(df[['Adj Close']])

# Build a neural network model
model = tf.keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=[X.shape[1]]),
    layers.Dense(64, activation='relu'),
    layers.Dense(1)
])
model.compile(optimizer='rmsprop', loss='mean_squared_error',
              metrics=['mean_absolute_error', 'mean_squared_error'])

# Train the model
model.fit(X, Y, epochs=100)

# Predict future stock price
predicted_price = scaler.inverse_transform(model.predict([[0]]))[0][0]
print(f'Predicted Price: {predicted_price}')

# Optional: Plotting the model's predictions (for visualization purposes)
plt.figure(figsize=(10,6))
predicted_prices = model.predict(X)
plt.plot(df['Adj Close'].index, scaler.inverse_transform(predicted_prices), label='Predicted')
plt.plot(df['Adj Close'], label='Actual')
plt.title(f'{symbol} Stock Price Prediction')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()