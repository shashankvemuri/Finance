import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

symbol = 'BAC'

num_of_years = 1
start = dt.date.today() - dt.timedelta(days=365*num_of_years)
end = dt.date.today()

df = yf.download(symbol,start,end)
df['Returns'] = df['Adj Close'].pct_change()
df = df.dropna()
print(df.head())

returns = np.array(df['Returns'])
wins = returns[returns > 0]
losses = returns[returns <= 0]

W = len(wins) / len(returns)
R = np.mean(wins) / np.abs(np.mean(losses))

Kelly = W - ( (1 - W) / R )
print('Kelly Criterion: {}%'.format(np.round(Kelly, 3)))