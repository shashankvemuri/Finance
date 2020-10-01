import numpy as np
import pandas as pd
import yfinance
import matplotlib.pyplot as plt
import datetime as dt
pd.set_option('display.max_columns', None)

stock = input('Enter a ticker: ')
start = dt.date.today() - dt.timedelta(days=1)

ticker = yfinance.Ticker(stock)
df = ticker.history(interval="1d")
last_day = df.tail(1).copy().drop(columns=['Dividends', 'Stock Splits'])

last_day['Pivot'] = (last_day['High'] + last_day['Low'] + last_day['Close'])/3
last_day['R1'] = 2*last_day['Pivot'] - last_day['Low']
last_day['S1'] = 2*last_day['Pivot'] - last_day['High']
last_day['R2'] = last_day['Pivot'] + (last_day['High'] - last_day['Low'])
last_day['S2'] = last_day['Pivot'] - (last_day['High'] - last_day['Low'])
last_day['R3'] = last_day['Pivot'] + 2*(last_day['High'] - last_day['Low'])
last_day['S3'] = last_day['Pivot'] - 2*(last_day['High'] - last_day['Low'])
print (last_day)

data = yfinance.download(tickers=stock, period="1d", interval="1m")
df = data['Close']

fig, ax = plt.subplots()
plt.rcParams['figure.figsize'] = (15, 10)
plt.plot(df)
plt.axhline(last_day['R1'].tolist()[0], color='b', label='Resistance 1')
plt.axhline(last_day['S1'].tolist()[0], color='b', label='Support 1')
plt.axhline(last_day['R2'].tolist()[0], color='green', label='Resistance 2')
plt.axhline(last_day['S2'].tolist()[0], color='green', label='Support 2')
plt.axhline(last_day['R3'].tolist()[0], color='r', label='Resistance 3')
plt.axhline(last_day['S3'].tolist()[0], color='r', label='Support 3')
plt.legend()
plt.title('{} - {}'.format(stock.upper(), start))
plt.xlabel('Time')
plt.ylabel('Price')
plt.show()