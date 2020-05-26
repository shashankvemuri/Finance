import math
from pandas_datareader import DataReader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import datetime

#from keras.models import Sequential
#from keras.layers import Dense, LSTM
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM

import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

#get the stock quote
stock = input("Enter a stock ticker: ")
start_date = datetime.datetime.now() - datetime.timedelta(days=3650)
end_date = datetime.date.today()

df = DataReader(stock, "yahoo", start_date, end_date)

#create a new DF with only the close column
data = df.filter(['Close'])
#convert DF to numpy array
dataset = data.values
#get the number of rows to train the model on
train_data_len = math.ceil(len(dataset)*.8)


#scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

#create training dataset
#create scaled training dataset
train_data = scaled_data[0:train_data_len, :]
#split data into x_train and y_train dataset
x_train=[]
y_train=[]

for i in range(60,len(train_data)):
  x_train.append(train_data[i-60:i, 0])
  y_train.append(train_data[i, 0])
  if i<=61:
    #print(x_train)
    #print(y_train)
    print()
    

#convert x_train and y_train to numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)

#reshape the data to 3 dimension
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
x_train.shape

#build LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(LSTM(50,return_sequences=False))
# model.add(Dense(6, init = 'uniform', activation = 'relu', input_shape = (11,)))
model.add(Dense(25))
model.add(Dense(1))

#compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

#train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

#create test dataset
#create new array containing scaled values from index (1663-60) to 2077
test_data = scaled_data[train_data_len-60:, :]
#create dataset x_test, y_test
x_test = []
y_test = dataset[train_data_len:, :]
for i in range(60,len(test_data)):
  x_test.append(test_data[i-60:i, 0])
  
#convert data to numpy array
x_test = np.array(x_test)

#reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

#get the models predicted price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean((predictions-y_test)**2))

#plot the data
train = data[:train_data_len]
valid = data[train_data_len:]
valid['Predictions'] = predictions
#visualize
plt.figure(figsize=(16,8))
plt.title('Model')
plt.xlabel('Date', fontsize=16)
plt.ylabel('Close Price USD', fontsize=16)
plt.plot(train['Close'])
plt.plot(valid[['Close','Predictions']])
plt.legend(['Train','Val','Prediction'],loc='lower right')
plt.show()

print (valid)

#use latest data, convert to numpy array
last_60day = data[-60:].values
#scale the data
last_60day_scaled = scaler.transform(last_60day)
#create empty list, append the past 60 days
xx_test = []
xx_test.append(last_60day_scaled)
#convert to numpy array
xx_test = np.array(xx_test)
#reshape data
xx_test = np.reshape(xx_test, (xx_test.shape[0], xx_test.shape[1],1))
#get predicted price
pred = model.predict(xx_test)
pred = scaler.inverse_transform(pred)
print(pred)
