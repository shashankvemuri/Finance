import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler

symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days=394)
end = dt.date.today()

df = yf.download(symbol,start,end)

df['Open_Close'] = (df['Open'] - df['Adj Close'])/df['Open']
df['High_Low'] = (df['High'] - df['Low'])/df['Low']
df['Increase_Decrease'] = np.where(df['Volume'].shift(-1) > df['Volume'],1,0)
df['Buy_Sell_on_Open'] = np.where(df['Open'].shift(-1) > df['Open'],1,0)
df['Buy_Sell'] = np.where(df['Adj Close'].shift(-1) > df['Adj Close'],1,0)
df['Returns'] = df['Adj Close'].pct_change()
df = df.dropna()

model = tf.keras.Sequential([keras.layers.Dense(units=1, input_shape=[1])])
model.compile(optimizer='sgd', loss='mean_squared_error')

X = np.array(df['Returns'], dtype = float) # Feature
Y = np.array(df['Adj Close'], dtype = float) # Target
model.fit(X, Y, epochs=100)

scaler = MinMaxScaler()
normalized_X = scaler.fit_transform(np.array(df['Returns']).reshape(271,-1))
X = np.array(normalized_X, dtype = float)
normalized_Y = scaler.fit_transform(np.array(df['Adj Close']).reshape(271,-1))
Y = np.array(normalized_Y, dtype = float)

def build_model():
    model = keras.Sequential([
    layers.Dense(64, activation=tf.nn.relu, input_shape=[len(train_dataset.keys())]),
    layers.Dense(64, activation=tf.nn.relu),
    layers.Dense(1)])

    model.compile(loss='mean_squared_error',
                optimizer=optimizer,
                metrics=['mean_absolute_error', 'mean_squared_error'])
    return model

print('Predicted Price: ' + model.predict([0])[0][0])