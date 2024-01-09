# Import necessary libraries
import math
import datetime 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from pandas_datareader import data as pdr
import yfinance as yf

# Prompt user to enter a stock ticker
stock = input("Enter a stock ticker: ")

# Setup for fetching stock data
num_of_years = 10
start_date = datetime.datetime.now() - datetime.timedelta(days=365.25 * num_of_years)
end_date = datetime.date.today()

# Fetch stock data
yf.pdr_override()
df = pdr.get_data_yahoo(stock, start=start_date, end=end_date)
data = df.filter(['Close'])
dataset = data.values
train_data_len = math.ceil(len(dataset) * .8)

# Scale data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

# Create training data
x_train, y_train = [], []
for i in range(60, len(train_data)):
    x_train.append(scaled_data[i-60:i, 0])
    y_train.append(scaled_data[i, 0])
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# LSTM network
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)),
    LSTM(50, return_sequences=False),
    Dense(25),
    Dense(1)
])
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=5)

# Create testing dataset
test_data = scaled_data[train_data_len - 60:, :]
x_test = [test_data[i-60:i, 0] for i in range(60, len(test_data))]
x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Predictions
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)
rmse = np.sqrt(mean_squared_error(data[train_data_len:].values, predictions))

# Plot the data
train = data[:train_data_len]
valid = data[train_data_len:].assign(Predictions=predictions)
plt.figure(figsize=(16,8))
plt.title(f"{stock.upper()} Close Price")
plt.xlabel('Date', fontsize=16)
plt.ylabel('Close Price (USD)', fontsize=16)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Valid', 'Prediction'], loc='lower right')
plt.show()

# Predict next day price
last_60_days = data[-60:].values
last_60_days_scaled = scaler.transform(last_60_days)
X_test_next = np.array([last_60_days_scaled])
X_test_next = np.reshape(X_test_next, (X_test_next.shape[0], X_test_next.shape[1], 1))
predicted_price_next_day = scaler.inverse_transform(model.predict(X_test_next))[0][0]
print(f"The predicted price for the next trading day is: {predicted_price_next_day:.2f}")

# Display RMSE
print(f"The root mean squared error is {rmse:.2f}")