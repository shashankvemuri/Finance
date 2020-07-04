import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LinearRegression
import datetime as dt

symbol = 'AAPL'

start = dt.date.today() - dt.timedelta(days=394)
end = dt.date.today()

df = yf.download(symbol,start,end)
df['Open_Close'] = (df['Open'] - df['Adj Close'])/df['Open']
df['High_Low'] = (df['High'] - df['Low'])/df['Low']
df['Increase_Decrease'] = np.where(df['Volume'].shift(-1) > df['Volume'],1,0)
df['Buy_Sell_on_Open'] = np.where(df['Open'].shift(-1) > df['Open'],1,0)
df['Buy_Sell'] = np.where(df['Adj Close'].shift(-1) > df['Adj Close'],1,0)
df['Returns'] = df['Adj Close'].pct_change()
df = df.dropna()

X = np.array(df['Open']).reshape(271,-1)
Y = np.array(df['Adj Close']).reshape(271,-1)

lr = LinearRegression()
lr.fit(X, Y)

print('Estimate intercept coefficient:', lr.intercept_)
print('Number of coefficients:', len(lr.coef_))
print('Accuracy Score:', lr.score(X, Y))

lr.predict(X)

plt.figure(figsize=(12,8))
plt.scatter(df['Adj Close'], lr.predict(X))
plt.plot(X, lr.predict(X), color = 'red')
plt.xlabel('Prices')
plt.ylabel('Predicted Prices')
plt.grid()
plt.title('Prices vs Predicted Prices')
plt.show()