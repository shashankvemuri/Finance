# Import necessary libraries
import os
import datetime
import requests
import yfinance as yf
from numpy import array, hstack
from sklearn.model_selection import train_test_split
from keras.models import Sequential, model_from_json
from keras.layers import LSTM, Dense, Flatten, TimeDistributed, Conv1D, MaxPooling1D
from keras import callbacks

# Setup data for LSTM model
def setup_data(symbol, data_len, seq_len):
    # Get start and end dates for data
    end = datetime.datetime.today().strftime('%Y-%m-%d')
    start = datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=(data_len / 0.463))

    # Download and normalize data using Yahoo Finance API
    orig_dataset = yf.download(symbol, start, end)
    close = orig_dataset['Close'].values
    open_ = orig_dataset['Open'].values
    high = orig_dataset['High'].values
    low = orig_dataset['Low'].values
    dataset, minmax = normalize_data(orig_dataset)

    # Convert dataset into sequences of length seq_len
    cols = dataset.columns.tolist()
    data_seq = list()
    for i in range(len(cols)):
        if cols[i] < 4:
            data_seq.append(dataset[cols[i]].values)
            data_seq[i] = data_seq[i].reshape((len(data_seq[i]), 1))
    data = hstack(data_seq)
    X, y = split_sequences(data, seq_len)

    # Reshape input data to fit the LSTM model
    n_seq, n_steps, n_features = X.shape
    X = X.reshape((n_seq, 1, n_steps, n_features))
    true_y = [[y[i][0], y[i][1]] for i in range(len(y))]

    return X, array(true_y), n_features, minmax, seq_len, close, open_, high, low

# Normalize dataset between 0 and 1
def normalize_data(dataset):
    cols = dataset.columns.tolist()
    col_name = [0] * len(cols)
    for i in range(len(cols)):
        col_name[i] = i
    dataset.columns = col_name

    for column in dataset:
        dataset = dataset.astype({column: 'float32'})

    minmax = []
    for i in range(len(cols)):
        col_values = dataset[col_name[i]]
        value_min = min(col_values)
        value_max = max(col_values)
        minmax.append([value_min, value_max])

    for column in dataset:
        values = dataset[column].values
        for i in range(len(values)):
            values[i] = (values[i] - minmax[column][0]) / (minmax[column][1] - minmax[column][0])
        dataset[column] = values

    return dataset, minmax

# Split dataset into input sequences and their corresponding output
def split_sequences(sequences, seq_len):
    X, y = [], []
    for i in range(len(sequences)):
        end_ix = i + seq_len
        if end_ix > len(sequences) - 1:
            break
        seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix, :]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)

# Set up training and testing datasets
def setup_datasets(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    return X_train, X_test, y_train, y_test

# Initialize model
def initialize_network(n_steps,n_features,optimizer):
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1, activation='relu'), input_shape=(None, n_steps, n_features)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(2))
    model.compile(optimizer=optimizer, loss='mse')
    return model

# Train model
def train_model(X_train,y_train,model,epochs):
    dirx = ''
    os.chdir(dirx)
    h5='stocks'+'_best_model'+'.h5'
    checkpoint = callbacks.ModelCheckpoint(h5, monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto', period=1)
    earlystop = callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=epochs * 1/4, verbose=0, mode='auto', baseline=None, restore_best_weights=True)
    callback = [earlystop,checkpoint] 
    json = 'stocks'+'_best_model'+'.json'
    model_json = model.to_json()
    with open(json, "w") as json_file:
        json_file.write(model_json)
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=len(X_train)//4, verbose=2,validation_split = 0.3, callbacks = callback)
    return history

# Load keras model
def load_keras_model(dataset,model,loss,optimizer):
    dirx = ''
    os.chdir(dirx)
    json_file = open(dataset+'_best_model'+'.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.compile(optimizer=optimizer, loss=loss, metrics = None)
    model.load_weights(dataset+'_best_model'+'.h5')
    return model

# Evaluate keras model
def evaluation(exe_time,X_test, y_test,X_train, y_train,history,model,optimizer,loss):
    model = load_keras_model('stocks',model,loss,optimizer)
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    eval_test_loss = round(100-(test_loss*100),1)
    eval_train_loss = round(100-(train_loss*100),1)
    eval_average_loss = round((eval_test_loss + eval_train_loss)/2,1)
    print("--- Training Report ---")
    print('Execution time: ',round(exe_time,2),'s')
    print('Testing Accuracy:',eval_test_loss,'%')
    print('Training Accuracy:',eval_train_loss,'%')
    print('Average Network Accuracy:',eval_average_loss,'%')
    return model,eval_test_loss

# Use model to predict
def market_predict(model,minmax,seq_len,n_features,n_steps,data,test_loss):
    pred_data = data[-1].reshape((len(data[-1]),1, n_steps, n_features))
    pred = model.predict(pred_data)[0]
    appro_loss = list()
    for i in range(len(pred)):
        pred[i] = pred[i] * (minmax[i][1] - minmax[i][0]) + minmax[i][0]
        appro_loss.append(((100-test_loss)/100) * (minmax[i][1] - minmax[i][0]))
    return pred,appro_loss

# Alpaca API setup
BASE_URL = 'https://paper-api.alpaca.markets'
API_KEY = "*****************"
SECRET_KEY = "************************************"
ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID':API_KEY,'APCA-API-SECRET-KEY':SECRET_KEY}

# Send an order to the Alpaca account
def create_order(pred_price,company,test_loss,appro_loss):
    open_price,close_price = pred_price[0],pred_price[1]
    if open_price > close_price:
        side = 'sell'
    elif open_price < close_price:
        side = 'buy'
    if side == 'buy':
        order = {
            'symbol':company,
            'qty':round(20*(test_loss/100)),
            'type':'stop_limit',
            'time_in_force':'day',
            'side': 'buy',
            'take_profit': close_price + appro_loss,
            'stop_loss': close_price - appro_loss
                }
    elif side == 'sell':
        order = {
            'symbol':company,
            'qty':round(20*(test_loss/100)),
            'type':'stop_limit',
            'time_in_force':'day',
            'side': 'sell',
            'take_profit':close_price - appro_loss,
            'stop_loss':close_price + appro_loss
                }
    r = requests.post(ORDERS_URL, json = order,headers = HEADERS)
    print(r.content)

# Call setup data function
setup_data('AAPL', 365, 10)