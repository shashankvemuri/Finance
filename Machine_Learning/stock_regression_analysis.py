# Import dependencies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import seaborn as sns
import datetime as dt
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Set up stock data
stock = 'AAPL'
start_date = dt.date.today() - dt.timedelta(days=365 * 10)
end_date = dt.date.today()

# Download and load data
data = yf.download(stock, start_date, end_date)

# Drop unused columns
data = data.drop(columns=['Adj Close'])

# Split data into X and y
X = data.drop(['Close'], axis=1)
y = data['Adj Close']

# Split X and y into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

# Create a linear regression model
regression_model = LinearRegression()

# Train the model
regression_model.fit(X_train, y_train)

# Get the intercept for the model
intercept = regression_model.intercept_

print("The intercept for our model is: {}".format(intercept))

# Test the model
score = regression_model.score(X_test, y_test)
print("The score for our model is: {}".format(score))

# Predict the next day's price
latest_data = data.tail(1).values.tolist()
next_day_price = regression_model.predict(latest_data)[0]

print("The predicted price for the next trading day is: {}".format(next_day_price))