# Import necessary libraries
import os
import sys
import math
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import yfinance as yf

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import ta_functions as ta

# Prompt user to enter a stock ticker
stock = input("Enter a stock ticker: ")

# Setup for fetching stock data
num_of_years = 10
start_date = datetime.datetime.now() - datetime.timedelta(days=365.25 * num_of_years)
end_date = datetime.date.today()

# Fetch stock data
df = yf.download(stock, start=start_date, end=end_date)

# Engineer financial features: returns, volatility, and momentum indicators
df['Return'] = df['Close'].pct_change()
df['Return_5d'] = df['Close'].pct_change(5)
df['Return_10d'] = df['Close'].pct_change(10)
df['Volatility_10d'] = ta.STDDEV(df['Return'], timeperiod=10)
df['Volatility_20d'] = ta.STDDEV(df['Return'], timeperiod=20)
df['Momentum_10d'] = ta.MOM(df['Close'], timeperiod=10)
df['ROC_10d'] = ta.ROC(df['Close'], timeperiod=10)
df['RSI_14d'] = ta.RSI(df['Close'], timeperiod=14)
df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()

# Target: next-day return
df['Target'] = df['Return'].shift(-1)
df.dropna(inplace=True)

# Prepare features and target
feature_cols = [
    'Return', 'Return_5d', 'Return_10d', 'Volatility_10d', 'Volatility_20d',
    'Momentum_10d', 'ROC_10d', 'RSI_14d', 'Volume_Ratio'
]
X = df[feature_cols]
y = df['Target']

# Chronological train/test split (no shuffling, avoids lookahead bias on time series data)
train_data_len = math.ceil(len(X) * .8)
x_train, x_test = X[:train_data_len], X[train_data_len:]
y_train, y_test = y[:train_data_len], y[train_data_len:]

# Gradient Boosting model
model = GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42)
model.fit(x_train, y_train)

# Predictions
predictions = model.predict(x_test)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

# Plot actual vs predicted next-day returns
plt.figure(figsize=(16,8))
plt.title(f"{stock.upper()} Gradient Boosting: Actual vs Predicted Next-Day Returns")
plt.xlabel('Date', fontsize=16)
plt.ylabel('Next-Day Return', fontsize=16)
plt.plot(y_test.index, y_test, label='Actual')
plt.plot(y_test.index, predictions, label='Predicted')
plt.legend(loc='lower right')
plt.show()

# Plot feature importances
plt.figure(figsize=(16,8))
plt.title(f"{stock.upper()} Gradient Boosting Feature Importances")
plt.bar(feature_cols, model.feature_importances_)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Predict next day's return using the most recent feature row
last_row = X.iloc[[-1]]
predicted_return_next_day = model.predict(last_row)[0]
last_close = df['Close'].iloc[-1]
predicted_price_next_day = last_close * (1 + predicted_return_next_day)
print(f"The predicted return for the next trading day is: {predicted_return_next_day:.4f}")
print(f"The predicted price for the next trading day is: {predicted_price_next_day:.2f}")

# Display RMSE
print(f"The root mean squared error is {rmse:.4f}")
