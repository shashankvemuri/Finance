import pandas as pd
import numpy as np
import yfinance as yf
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import datetime

# Setuo
yf.pdr_override()
plt.rcParams['figure.figsize'] = [15, 10]
plt.rc('font', size=14) 

# Parameters
ticker = input('Enter a ticker: ')
num_of_years = .2

start_date = datetime.date.today() - datetime.timedelta(days = int(365.25*num_of_years))
end_date = datetime.date.today()

# Dataframe
df = pdr.get_data_yahoo(ticker, start_date, end_date).reset_index()
df['Date'] = df['Date'].apply(mpl_dates.date2num)
df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]

# Calculate support and resistance 
def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

  return support

def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2] 

  return resistance

levels = []
for i in range(2,df.shape[0]-2):
  if isSupport(df,i):
    levels.append((i,df['Low'][i]))
  elif isResistance(df,i):
    levels.append((i,df['High'][i]))

# Plot support and resistance 
def plot_all():
  fig, ax = plt.subplots()
  plt.title(f'Support and Resistance for {ticker.upper()}')
  plt.xlabel('Date')
  plt.ylabel('Price')
  candlestick_ohlc(ax,df.values,width=0.6, colorup='green', colordown='red', alpha=0.8)

  date_format = mpl_dates.DateFormatter('%d %b %Y')
  ax.xaxis.set_major_formatter(date_format)
  fig.autofmt_xdate()

  fig.tight_layout()

  for level in levels:
    plt.hlines(level[1],xmin=df['Date'][level[0]], xmax=max(df['Date']),colors='blue')
  fig.show()

s =  np.mean(df['High'] - df['Low'])

# Take out close support and resistance 
def isFarFromLevel(l):
  return np.sum([abs(l-x) < s  for x in levels]) == 0


levels = []
for i in range(2,df.shape[0]-2):
  if isSupport(df,i):
    l = df['Low'][i]
    w = 'Support'

    if isFarFromLevel(l):
      levels.append((i,l))

  elif isResistance(df,i):
    l = df['High'][i]
    w = 'Resistance'

    if isFarFromLevel(l):
      levels.append((i,l))

dates = [x[0] for x in levels]
prices = [x[1] for x in levels]

which = []
for date, price in zip(dates, prices):
    for i in range(2,df.shape[0]-2):
      if price == df['Low'][i]:
        w = 'Support'
    
      elif price == df['High'][i]:
        w = 'Resistance'

      else:
          continue
    which.append(w)

new_dates = []
for date in dates:
    new_date = start_date + datetime.timedelta(days = date)
    new_dates.append(new_date)

frame = pd.DataFrame(zip(new_dates, which, prices), columns = ['Date', 'Support or Resistance', 'Price']).set_index('Date')
print (frame)

plot_all()