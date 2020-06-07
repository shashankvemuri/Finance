import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

# input
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days = 365*2)
end = dt.date.today()

# Read data 
df = yf.download(symbol, start=start, end=end)

df['% Change'] = df['Adj Close'].pct_change() # pct_change : percent profit rate
df['P_AdjClose'] = df['Adj Close'].shift(1) # P_Adj Close : previous Close
df['L_Profit'] = np.log(df['Adj Close'] / df['P_AdjClose']) # L_Profit : Log Profit Rate
df['MA_50'] = df['Adj Close'].rolling(center=False, window=50).mean()
df['MA_200'] = df['Adj Close'].rolling(center=False, window=200).mean()
df['diff'] = df['MA_50'] - df['MA_200']

df = df[['Volume', 'Adj Close', 'MA_50', 'MA_200', 'diff']]

prev_key = prev_val = 0

for key, val in df['diff'].iteritems():
  if val == 0:
    continue
  if val * prev_val < 0 and val > prev_val:
    print('[Golden]', key, val, df['Adj Close'][key])
  if val * prev_val < 0 and val < prev_val:
    print('[Death]', key, val, df['Adj Close'][key])
  prev_key, prev_val = key, val


# ### 50-day Moving Average goes 'under' 200-day Moving Average is a "Death Cross."
# ### 50-day Moving Average goes 'over' 200-day Moving Average is a "Golden Cross."
df[['Adj Close', 'MA_50', 'MA_200']]['2018-08':].plot()

ax = df[['Adj Close', 'MA_50', 'MA_200']].plot(figsize=(18, 8))

prev_key = prev_val = 0

for key, val in df['diff'].iteritems():
  if val == 0:
    continue
    
    if val * prev_val < 0 and val > prev_val:
        ax.annotate('Golden', xy=(key, df['MA_200'][key]), xytext=(10,-30), 
                    textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
    elif val * prev_val < 0 and val < prev_val:
        ax.annotate('Death', xy=(key, df['MA_200'][key]), xytext=(10,30), 
                    textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
    
    prev_key, prev_val = key, val


# ## Plot Multi-colors of one line
df['Label'] = np.where(df['MA_50'] > df['MA_200'], 1, -1)

import matplotlib.patches as mpatches

df = df.dropna(axis=0, how='any')

fig, ax = plt.subplots(figsize=(14,7))

def plot_colors(group):
    global ax
    color = 'r' if (group['Label'] < 0).all() else 'g'
    lw = 2.0
    ax.plot(group.index, group['Adj Close'], c=color, linewidth=lw)

df.groupby((df['Label'].shift() * df['Label'] < 0).cumsum()).apply(plot_colors)

ax.plot(df.index, df['MA_50'], 'k--', label='MA-50')
ax.plot(df.index, df['MA_200'], 'b--', label='MA-200')
ax.set_ylabel('Price')
ax.set_xlabel('Date')
ma50 = mpatches.Patch(color='blue', label='MA-50')
ma200 = mpatches.Patch(color='black', label='MA-200')
ax.legend(handles=[ma50,ma200])
plt.show()

# ## Plot Intersection Points
short_term = 50
long_term = 200

signals = pd.DataFrame(index=df.index)
signals['position'] = 0.0

signals['Short_MA'] = df['Adj Close'].rolling(window=short_term, center=False).mean()
signals['Long_MA'] = df['Adj Close'].rolling(window=long_term, center=False).mean()

signals['position'][short_term:] = np.where(signals['Short_MA'][short_term:] 
                                            > signals['Long_MA'][short_term:], 1.0, 0.0)   

signals['intersection'] = signals['position'].diff()
print(signals)

fig = plt.figure(figsize=(14,7))

# Add a subplot and label for y-axis
ax = fig.add_subplot(111,  ylabel='Price in $')

# Plot the Adj Close price
df['Adj Close'].plot(ax=ax, color='b', lw=2.)

# Plot the short and long moving averages
signals[['Short_MA', 'Long_MA']].plot(ax=ax, lw=2.)

# Plot the Signal of Golden Cross
ax.plot(signals.loc[signals.intersection == 1.0].index, 
         signals.Short_MA[signals.intersection == 1.0],
         'o', markersize=10, color='gold', label='Golden Cross')
         
# Plot the Signal of Death Cross
ax.plot(signals.loc[signals.intersection == -1.0].index, 
         signals.Short_MA[signals.intersection == -1.0],
         'o', markersize=10, color='black', label='Death Cross')

ax.set_title('Golden Cross and Death Cross')
ax.legend(loc='best')
         
# Show the plot
plt.show()