import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

symbol = 'MSFT'
short_window = 40
initial_capital = 10000 # Starting Cash

num_of_years = 3
start = dt.date.today() - dt.timedelta(days=365*num_of_years)
end = dt.date.today()

df = yf.download(symbol,start,end)

df['Signal'] = 0
df['Short_MA'] = df['Adj Close'].rolling(window=20).mean()
df['Long_MA'] = df['Adj Close'].rolling(window=50).mean()

df['Signal'][short_window:] = np.where(df['Short_MA'][short_window:] > df['Long_MA'][short_window:], 1, 0)
df['Positions'] = df['Signal'].diff()

positions = pd.DataFrame(index=df.index).fillna(0.0)        
positions = 100 * df['Signal']

df['Daily P&L'] = df['Adj Close'].diff() * df['Signal']
df['Total P&L'] = df['Daily P&L'].cumsum()

positions = pd.DataFrame(index=df.index).fillna(0.0)
positions = 100 * df['Positions']
portfolio = pd.DataFrame(index=df.index)
portfolio['Holdings'] = positions*df['Adj Close']       
portfolio['Cash'] = initial_capital - portfolio['Holdings'].cumsum()
portfolio['Total'] = portfolio['Cash'] + positions.cumsum() * df['Adj Close']
portfolio['Returns'] = portfolio['Total'].pct_change()

fig = plt.figure(figsize=(14,10))
ax1 = plt.subplot(2, 1, 1)
df[['Short_MA', 'Long_MA']].plot(ax=ax1, lw=2.)
ax1.plot(df['Adj Close'])
ax1.plot(df.loc[df['Positions'] == 1.0].index, df.Short_MA[df['Positions'] == 1.0],'^', markersize=10, color='g', label='Long')
ax1.plot(df.loc[df['Positions'] == -1.0].index,  df.Short_MA[df['Positions'] == -1.0],'v', markersize=10, color='r', label='Short')
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.grid()
ax1.legend()

ax2 = plt.subplot(2, 1, 2)
ax2.plot(portfolio['Total'])
ax2.set_ylabel('Portfolio Value')
ax2.set_xlabel('Date')
ax2.legend()
ax2.grid()
plt.show()