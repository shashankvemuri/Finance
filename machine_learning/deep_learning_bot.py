# Import necessary libraries
import datetime
import requests
import yfinance as yf
import numpy as np
import pandas as pd
from numpy import array, hstack
from sklearn.model_selection import train_test_split
from keras.models import Sequential, model_from_json
from keras.layers import LSTM, Dense, Flatten, TimeDistributed, Conv1D, MaxPooling1D
from keras import callbacks

# Function to setup data for LSTM model
def setup_data(symbol, data_len, seq_len):
    # Get dates for data
    end = datetime.datetime.today().strftime('%Y-%m-%d')
    start = (datetime.datetime.strptime(end, '%Y-%m-%d') - 
             datetime.timedelta(days=(data_len / 0.463))).strftime('%Y-%m-%d')

    # Download and normalize data
    data = yf.download(symbol, start, end)
    dataset, minmax = normalize_data(data)

    # Convert dataset into sequences
    data_seq = [dataset[col].values.reshape((len(dataset[col]), 1)) for col in dataset.columns]
    data = hstack(data_seq)
    X, y = split_sequences(data, seq_len)

    # Reshape input data for LSTM model
    X = X.reshape((X.shape[0], 1, X.shape[1], X.shape[2]))
    true_y = [[y[i][0], y[i][1]] for i in range(len(y))]

    return X, array(true_y), X.shape[2], minmax, seq_len, data

# Normalize dataset function
def normalize_data(dataset):
    minmax = []
    for col in dataset.columns:
        min_val, max_val = dataset[col].min(), dataset[col].max()
        minmax.append([min_val, max_val])
        dataset[col] = (dataset[col] - min_val) / (max_val - min_val)
    return dataset, minmax

# Split dataset into sequences
def split_sequences(sequences, seq_len):
    X, y = [], []
    for i in range(len(sequences) - seq_len):
        X.append(sequences[i:i+seq_len, :])
        y.append(sequences[i + seq_len, :])
    return array(X), array(y)

# Initialize and compile LSTM model
def initialize_network(n_steps, n_features, optimizer='adam'):
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1, activation='relu'), 
                              input_shape=(None, n_steps, n_features)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(2))
    model.compile(optimizer=optimizer, loss='mse')
    return model

# Train LSTM model
def train_model(X_train, y_train, model, epochs=10):
    # Define callback for early stopping and saving the best model
    checkpoint = callbacks.ModelCheckpoint('best_model.h5', monitor='val_loss', 
                                           save_best_only=True, mode='auto', period=1)
    earlystop = callbacks.EarlyStopping(monitor='val_loss', patience=epochs//4, 
                                        restore_best_weights=True)
    # Train model
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=len(X_train)//4, 
                        verbose=2, validation_split=0.3, callbacks=[earlystop, checkpoint])
    return history

# Load trained LSTM model
def load_keras_model(model_file='best_model'):
    with open(f'{model_file}.json', 'r') as json_file:
        loaded_model_json = json_file.read()
    model = model_from_json(loaded_model_json)
    model.load_weights(f'{model_file}.h5')
    model.compile(optimizer='adam', loss='mse')
    return model

# Evaluate model performance
def evaluate_model(model, X_test, y_test, X_train, y_train):
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    return {'test_loss': test_loss, 'train_loss': train_loss}

# Main execution
X, y, n_features, minmax, seq_len, data = setup_data('AAPL', 365, 10)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
model = initialize_network(seq_len, n_features)
history = train_model(X_train, y_train, model, epochs=100)
model = load_keras_model()
performance = evaluate_model(model, X_test, y_test, X_train, y_train)
print(performance)

################################################################

# Alpaca API setup
BASE_URL = 'https://paper-api.alpaca.markets'
API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}

# Function to create an order using the Alpaca API
def create_order(symbol, qty, side, type_, time_in_force, limit_price=None, stop_price=None):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type_,
        "time_in_force": time_in_force
    }
    if limit_price:
        data["limit_price"] = limit_price
    if stop_price:
        data["stop_price"] = stop_price

    url = f"{BASE_URL}/v2/orders"
    r = requests.post(url, json=data, headers=HEADERS)
    return r.json()

# Example usage of create_order
# Modify the parameters based on your trading strategy
response = create_order('AAPL', 1, 'buy', 'market', 'gtc')
print(response)