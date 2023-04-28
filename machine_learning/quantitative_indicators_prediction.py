# Import dependencies
import pandas as pd
import datetime
from sklearn.model_selection import train_test_split
import numpy as np
from pandas_datareader import DataReader
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor

# Ticker of the stock to be analyzed
ticker = 'MCD'
# Start date of the stock data
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
# End date of the stock data
end_date = datetime.date.today()

# Download data for the given stock from Yahoo Finance API
df = DataReader(ticker, 'yahoo', start_date, end_date)

# Add Simple Moving Averages (SMA) for different periods to the dataframe
for sma_period in [5,10,20,50,100,200]:
    # Create column name
    indicator_name = "SMA_%d" % (sma_period)
    # Add SMA to dataframe
    df[indicator_name] = df['Close'].rolling(sma_period).mean()

# Add Bollinger Bands to the dataframe
df['BollingerBand_Up_20_2'] = df['Close'].rolling(20).mean() + 2*df['Close'].rolling(20).std()
df['BollingerBand_Down_20_2'] = df['Close'].rolling(20).mean() - 2*df['Close'].rolling(20).std()
df['BollingerBand_Up_20_1'] = df['Close'].rolling(20).mean() + df['Close'].rolling(20).std()
df['BollingerBand_Down_20_1'] = df['Close'].rolling(20).mean() - df['Close'].rolling(20).std()
df['BollingerBand_Up_10_1'] = df['Close'].rolling(10).mean() + df['Close'].rolling(10).std()
df['BollingerBand_Down_10_1'] = df['Close'].rolling(10).mean() - df['Close'].rolling(10).std()
df['BollingerBand_Up_10_2'] = df['Close'].rolling(10).mean() + 2*df['Close'].rolling(10).std()
df['BollingerBand_Down_10_2'] = df['Close'].rolling(10).mean() - 2*df['Close'].rolling(10).std()

# Add Donchian Channels to the dataframe
for channel_period in [5,10,20,50,100,200]:
    up_name = "Donchian_Channel_Up_%d" % (channel_period)
    down_name = "Donchian_Channel_Down_%d" % (channel_period)
    df[up_name] = df['High'].rolling(channel_period).max()
    df[down_name] = df['Low'].rolling(channel_period).min()

# Select data that will be used to train the model
newdata = df['Close'].to_frame()
# Add shifted versions of the data as additional features
for lag in [1,2,3,4,5,6,7,8,9,10]:
    shift = lag
    shifted = df.shift(shift)
    shifted.columns = [str.format("%s_shifted_by_%d" % (column ,shift)) for column in shifted.columns]
    newdata = pd.concat((newdata,shifted),axis=1)
    
# Forward lag
forward_lag = 5
newdata['target'] = newdata['Close'].shift(-forward_lag)
newdata = newdata.drop('Close',axis=1)
newdata = newdata.dropna()

# Create train and test data
X = newdata.drop("target",axis=1)
Y = newdata['target']
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

# Train the model
correlations = np.abs(X_train.corrwith(y_train))
features =  list(correlations.sort_values(ascending=False)[0:50].index)
X_train = X_train[features]
X_test = X_test[features]
lr = LinearRegression()
lr.fit(X_train,y_train)

# Get linear regression prediction
y_pred = lr.predict(X_test)

# Calculate mean absolute error
mean_absolute_error(y_test,y_pred)

# Plot scatter plot of test and predicted values
plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Linear regression")
plt.show()

# Random Forest Regressor
rf = RandomizedSearchCV(RandomForestRegressor(),
param_distributions =  {
                  'n_estimators':np.arange(10,500,5),
                  'max_features':np.arange(1,10,1)
               },
                  cv=5, n_iter = 20,
                  iid=False,random_state=0,refit=True,
                  scoring="neg_mean_absolute_error")
rf.fit(X_train,y_train)

# Gradient Boosting Regressor
gb = RandomizedSearchCV(GradientBoostingRegressor(),
param_distributions =  {
               'n_estimators':np.arange(10,500,5),
               'max_features':np.arange(1,10,1)
            },
          cv=5, n_iter = 20,
          iid=False,random_state=0,refit=True,
          scoring="neg_mean_absolute_error")
gb.fit(X_train,y_train)

# K Neighbor sRegressor
knn = GridSearchCV(KNeighborsRegressor(),
param_grid =  {
            'n_neighbors':np.arange(1,20,1),
            'weights':['distance','uniform']
            },
          cv=5, 
          iid=False,refit=True,
          scoring="neg_mean_absolute_error")
knn.fit(X_train,y_train)

# MLPRegressor
scaler = MinMaxScaler()
scaler.fit(X_train)
nnet = RandomizedSearchCV(MLPRegressor(max_iter=5000,learning_rate = 'adaptive',solver='sgd'),
param_distributions =  {
     'hidden_layer_sizes':[(x,) for x in np.arange(1,50,1)],
     'activation':['logistic','relu']
},
cv=5, n_iter = 20,
iid=False,random_state=0,refit=True,
scoring="neg_mean_absolute_error")

# Adjust train and test data
X = newdata.drop("target",axis=1)
Y = newdata['target']
train_size = int(X.shape[0]*0.7)
X_train = X[0:train_size]
y_train = Y[0:train_size]
X_test = X[train_size:]
y_test = Y[train_size:]

# Bagging Regressor
lr_bag = RandomizedSearchCV(BaggingRegressor(LinearRegression()),
param_distributions =  {
               'n_estimators':np.arange(10,500,5),
               'max_features':np.arange(1,10,1)
          },
          cv=5, n_iter = 20,
          iid=False,random_state=0,refit=True,
          scoring="neg_mean_absolute_error")
lr_bag.fit(X_train,y_train)

# Ada Boost Regressor
lr_boost = GridSearchCV(AdaBoostRegressor(LinearRegression()),
param_grid =  {
               'n_estimators':np.arange(20,500,5)
      },
      cv=5, 
      iid=False,refit=True,
      scoring="neg_mean_absolute_error")
lr_boost.fit(X_train,y_train)