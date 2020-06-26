import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import  RandomizedSearchCV,GridSearchCV
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor,BaggingRegressor,GradientBoostingRegressor,AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import datetime as dt

num_of_years = 40
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.datetime.now() 
ticker = 'MSFT'

df = DataReader(ticker, 'yahoo', start,  now)

df['Close'] = df['Adj Close']
df = df.drop("Adj Close",axis=1)

for sma_period in [5,10,20,50,100,200]:
    indicator_name = "SMA_%d" % (sma_period)
    df[indicator_name] = df['Close'].rolling(sma_period).mean()

# # Adding Bollinger bands
df['BollingerBand_Up_20_2'] = df['Close'].rolling(20).mean() + 2*df['Close'].rolling(20).std()
df['BollingerBand_Down_20_2'] = df['Close'].rolling(20).mean() - 2*df['Close'].rolling(20).std()
df['BollingerBand_Up_20_1'] = df['Close'].rolling(20).mean() + df['Close'].rolling(20).std()
df['BollingerBand_Down_20_1'] = df['Close'].rolling(20).mean() - df['Close'].rolling(20).std()
df['BollingerBand_Up_10_1'] = df['Close'].rolling(10).mean() + df['Close'].rolling(10).std()
df['BollingerBand_Down_10_1'] = df['Close'].rolling(10).mean() - df['Close'].rolling(10).std()
df['BollingerBand_Up_10_2'] = df['Close'].rolling(10).mean() + 2*df['Close'].rolling(10).std()
df['BollingerBand_Down_10_2'] = df['Close'].rolling(10).mean() - 2*df['Close'].rolling(10).std()

# # Adding Donchian channels
for channel_period in [5,10,20,50,100,200]:
    up_name = "Donchian_Channel_Up_%d" % (channel_period)
    down_name = "Donchian_Channel_Down_%d" % (channel_period)
    
    df[up_name] = df['High'].rolling(channel_period).max()
    df[down_name] = df['Low'].rolling(channel_period).min()

# # Creating input features
newdata = df['Close'].to_frame()
for lag in [1,2,3,4,5,6,7,8,9,10]:
    shift = lag
    shifted = df.shift(shift)
    shifted.columns = [str.format("%s_shifted_by_%d" % (column ,shift)) for column in shifted.columns]
    newdata = pd.concat((newdata,shifted),axis=1)

# # Creating target variable
forward_lag = 5

newdata['target'] = newdata['Close'].shift(-forward_lag)
newdata = newdata.drop('Close',axis=1)

newdata = newdata.dropna()

# # Training and test set
X = newdata.drop("target",axis=1)
Y = newdata['target']

train_size = int(X.shape[0]*0.7)

X_train = X[0:train_size]
y_train = Y[0:train_size]

X_test = X[train_size:]
y_test = Y[train_size:]

# # Feature selection via Pearson correlation coeffficient
correlations = np.abs(X_train.corrwith(y_train))
features =  list(correlations.sort_values(ascending=False)[0:50].index)
print(features)

X_train = X_train[features]
X_test = X_test[features]

# # Linear regression
lr = LinearRegression()
lr.fit(X_train,y_train)
y_pred = lr.predict(X_test)

print ('\nLinear Regression')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Linear regression (with non-random train/test split)")
plt.show()

# # Random Forest Regression
rf = RandomizedSearchCV(RandomForestRegressor(),param_distributions =  {
                                'n_estimators':np.arange(10,500,5),
                                'max_features':np.arange(1,10,1)
                            },
                            cv=5, n_iter = 20,
                            iid=False,random_state=0,refit=True,
                            scoring="neg_mean_absolute_error")

rf.fit(X_train,y_train)
rf.best_params_
y_pred = rf.predict(X_test)

print ('\nRandom Forest Regression')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Random forest (with non-random train/test split)")
plt.show()

# # Gradient boosting regressor
gb = RandomizedSearchCV(GradientBoostingRegressor(),param_distributions =  {
                                'n_estimators':np.arange(10,500,5),
                                'max_features':np.arange(1,10,1)
                            },
                            cv=5, n_iter = 20,
                            iid=False,random_state=0,refit=True,
                            scoring="neg_mean_absolute_error")

gb.fit(X_train,y_train)
gb.best_params_
y_pred = gb.predict(X_test)

print ('\nGradient Boosting Regressor')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Gradient boosting regressor (with non-random train/test split)")
plt.show()

# # K Nearest Neighbors
knn = GridSearchCV(KNeighborsRegressor(),param_grid =  {
                                'n_neighbors':np.arange(1,20,1),
                                'weights':['distance','uniform']
                            },
                            cv=5, 
                            iid=False,refit=True,
                            scoring="neg_mean_absolute_error")

knn.fit(X_train,y_train)
knn.best_params_
y_pred = knn.predict(X_test)

print ('\nK Nearest Neighbors')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("KNN (with non-random train/test split)")
plt.show()

# # Neural network
scaler = MinMaxScaler()
scaler.fit(X_train)

nnet = RandomizedSearchCV(MLPRegressor(max_iter=5000,learning_rate = 'adaptive',solver='sgd'),param_distributions =  {
                                'hidden_layer_sizes':[(x,) for x in np.arange(1,50,1)],
                                'activation':['logistic','relu']
                            },
                            cv=5, n_iter = 20,
                            iid=False,random_state=0,refit=True,
                            scoring="neg_mean_absolute_error")

nnet.fit(scaler.transform(X_train),y_train)

y_pred = nnet.predict(scaler.transform(X_test))
nnet.best_params_

print ('\nNeural Network')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Neural network (with non-random train/test split)")
plt.show()

# # Linear regression with bagging
lr_bag = RandomizedSearchCV(BaggingRegressor(LinearRegression()),param_distributions =  {
                                'n_estimators':np.arange(10,500,5),
                                'max_features':np.arange(1,10,1)
                            },
                            cv=5, n_iter = 20,
                            iid=False,random_state=0,refit=True,
                            scoring="neg_mean_absolute_error")

lr_bag.fit(X_train,y_train)
y_pred = lr_bag.predict(X_test)
lr_bag.best_params_

print ('\nLinear Regression with bagging')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Linear regression with bagging (with non-random train/test split)")
plt.show()

# # Linear regression with boosting
lr_boost = GridSearchCV(AdaBoostRegressor(LinearRegression()),param_grid =  {
                                'n_estimators':np.arange(20,500,5)
                            },
                            cv=5, 
                            iid=False,refit=True,
                            scoring="neg_mean_absolute_error")

lr_boost.fit(X_train,y_train)
y_pred = lr_boost.predict(X_test)
lr_boost.best_params_

print ('\nLinear Regression with boosting')
print(mean_absolute_error(y_test,y_pred))

plt.scatter(y_test,y_pred)
plt.xlabel("Real")
plt.ylabel("Predicted")
plt.title("Linear regression with boosting (with non-random train/test split)")
plt.show()