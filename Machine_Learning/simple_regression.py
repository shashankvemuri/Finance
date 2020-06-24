# Simple Linear Regression Model 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

stock = 'AAPL'
start = dt.date.today() - dt.timedelta(days = 365*10)
end = dt.date.today()

data = yf.download(stock, start, end)
data.head()

df = data.reset_index()
df.head()

X = df.drop(['Date','Close'], axis=1, inplace=True)
y = df[['Adj Close']]

df = df.as_matrix()

# Split X and y into X_
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.25,  random_state=0)

regression_model = LinearRegression()
regression_model.fit(X_train, y_train)

intercept = regression_model.intercept_[0]

print("The intercept for our model is {}".format(intercept))

regression_model.score(X_test, y_test)

y_predict = regression_model.predict(X_test)

regression_model_mse = mean_squared_error(y_predict, y_test)

print ('The mean squared error is ' + str(math.sqrt(regression_model_mse)))

# input the latest Open, High, Low, Close, Volume
# predicts the next day price
data = data.drop(columns = ['Adj Close'])
print ('The predicted price for the next trading day is ' + str(regression_model.predict(data.tail(1).values.tolist())[0][0]))

