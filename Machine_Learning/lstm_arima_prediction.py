# # Importing the libraries
import math
import datetime
import warnings
import numpy as np
from math import sqrt
import matplotlib as mpl
import matplotlib.pyplot as plt
from keras.models import Sequential
from pandas.plotting import lag_plot
from keras.layers import Dense, LSTM
from pandas_datareader import DataReader
from statsmodels.tsa.arima_model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

warnings.filterwarnings('ignore')

ticker = 'TSLA'
start_date = datetime.datetime.now() - datetime.timedelta(days=3650)
end_date = datetime.date.today()

# # Fetching the historic prices 
df = DataReader(ticker, 'yahoo', start_date, end_date)

# # Plotting the data
plt.figure(figsize=(16,8))
plt.title(f'{ticker} Close Price History')
plt.plot(df['Close'],linewidth=2)
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

last= df.tail(365)
plt.figure(figsize=(16,8))
plt.title(f"{ticker}'s Daily Returns")
returns = last['Close'] / last['Close'].shift(1) - 1
returns.plot(label='returns %',linewidth=1)
plt.xlabel('Date', fontsize=18)
plt.ylabel('Returns (%)', fontsize=18)
plt.legend(loc='upper left')

mavg50 = df['Close'].rolling(window=50).mean()
mavg200 = df['Close'].rolling(window=20).mean()
mpl.rc('figure', figsize=(16,8))

df['Close'].plot(label=f'{ticker}',linewidth=1)
mavg50.plot(label='50 day moving average',linewidth=1)
mavg200.plot(label='200 day moving average',linewidth=1)
plt.legend(loc='upper left')
plt.title(f"{ticker} - 50 vs 200 day Moving Average")


# # LSTM Model Building
#Create a new dataframe with only the 'Close column
data = df.filter(['Close'])
dataset = data.values

#Using 80% of the data as traning data
training_data_len = math.ceil( len(dataset) * .8 )

#Scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

#Create the training data set
train_data = scaled_data[0:training_data_len , :]

#Split the data into x_train and y_train data sets
x_train = []
y_train = []
for i in range(60, len(train_data)):
  x_train.append(train_data[i-60:i, 0])
  y_train.append(train_data[i, 0])

#Creating numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

#Creating the Neural Network - LSTM
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences= False))
model.add(Dense(25))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, batch_size=5, epochs=5)

#Creating the test set
test_data = scaled_data[training_data_len - 60: , :]
x_test = []
y_test = dataset[training_data_len:, :]
for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i, 0])
x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

#Get predictions
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#Root mean squared error 
rmse=sqrt(mean_squared_error(predictions, y_test))
print ('\n')
print (f'The root mean squared error is {rmse}')

#Plot the data
train = data[900:training_data_len]
valid = data[training_data_len:]

valid['Predictions'] = predictions
plt.figure(figsize=(24,10))
plt.title(f'{ticker} Actual vs Predicted Prices')
plt.xlabel('Date', fontsize=15)
plt.ylabel('Close Price USD ($)', fontsize=15)
plt.plot(train['Close'],linewidth=1)
plt.plot(valid[['Close', 'Predictions']],linewidth=1.5)
plt.legend(['Historic Prices', 'Actual Prices', 'Predicted Prices'], loc='lower right')
plt.show()

#Creating a loop that checks if the prices have increased or decreased day vs. day+1 and seeing if actual vs predicted was correct
valid['Actual']= ''
valid['Predicted']= ''
valid['Recommendation']= ''

for i in range(0,len(valid)-1):
    if valid['Close'][i]<valid['Close'][i+1]:
        valid['Actual'][i+1]= "Increase"
    else:
        valid['Actual'][i+1]= "Decrease"
    if valid['Predictions'][i]<valid['Predictions'][i+1]:
        valid['Predicted'][i+1]= "Increase"
    else:
        valid['Predicted'][i+1]= "Decrease" 

for i in range(1,len (valid)):
    if valid['Actual'][i] == valid['Predicted'][i]:
        valid['Recommendation'][i]= "Correct"
    else:
        valid['Recommendation'][i]= "Incorrect"      

print(valid.tail(10))

# # Autocorrelation
plt.figure(figsize=(10,10))
lag_plot(df['Close'], lag=5)
plt.title(f'{ticker} Autocorrelation plot')

train_data, test_data = df[0:int(len(df)*0.8)], df[int(len(df)*0.8):]
plt.figure(figsize=(16,8))
plt.title(f'{ticker} Stock Price')
plt.xlabel('Dates')
plt.ylabel('Prices')
plt.plot(df['Close'], 'blue', label='Training Data')
plt.plot(test_data['Close'], 'green', label='Testing Data')

plt.legend()

# # Arima

#Calculating
def smape_kun(y_true, y_pred):
    return np.mean((np.abs(y_pred - y_true) * 200/ (np.abs(y_pred) + np.abs(y_true))))

train_ar = train_data['Close'].values
test_ar = test_data['Close'].values

history = [x for x in train_ar]
predictions = list()
for t in range(len(test_ar)):
    model = ARIMA(history, order=(5,1,0))
    model_fit = model.fit(disp=0)
    output = model_fit.forecast()
    yhat = output[0]
    predictions.append(yhat)
    obs = test_ar[t]
    history.append(obs)
    #print('predicted=%f, expected=%f' % (yhat, obs))
error = mean_squared_error(test_ar, predictions)
print('Testing Mean Squared Error: %.3f' % error)
error2 = smape_kun(test_ar, predictions)
print('Symmetric mean absolute percentage error: %.3f' % error2)

plt.figure(figsize=(12,7))
plt.plot(df['Close'], 'green', color='blue', label='Training Data')
plt.plot(test_data.index, predictions, color='green', marker='o', linestyle='dashed', 
         label='Predicted Price')
plt.plot(test_data.index, test_data['Close'], color='red', label='Actual Price',linewidth=1.5,)
plt.title(f"{ticker}'s Prices Prediction")
plt.xlabel('Dates')
plt.ylabel('Prices')

plt.legend()

plt.figure(figsize=(12,7))
plt.plot(test_data.index, predictions, color='green', marker='o', linestyle='dashed', 
         label='Predicted Price')
plt.plot(test_data.index, test_data['Close'], color='red', label='Actual Price',linewidth= 2)
plt.title(f'{ticker} Prices Prediction')
plt.xlabel('Dates')
plt.ylabel('Prices')

plt.legend()