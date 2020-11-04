import pandas as pd
import yfinance
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ticker = yfinance.Ticker("SPY")
df = ticker.history(period = '5mo')

for i in range(2,df.shape[0]):
  current = df.iloc[i,:]
  prev = df.iloc[i-1,:]
  prev_2 = df.iloc[i-2,:]

  realbody = abs(current['Open'] - current['Close'])
  candle_range = current['High'] - current['Low']

  idx = df.index[i]
  
  df.loc[idx,'Bullish Swing'] = current['Low'] > prev['Low'] and prev['Low'] < prev_2['Low']
  df.loc[idx,'Bearish Swing'] = current['High'] < prev['High'] and prev['High'] > prev_2['High']
  df.loc[idx,'Bullish Pinbar'] = realbody <= candle_range/3 and  min(current['Open'], current['Close']) > (current['High'] + current['Low'])/2 and current['Low'] < prev['Low']
  df.loc[idx,'Bearish Pinbar'] = realbody <= candle_range/3 and max(current['Open'] , current['Close']) < (current['High'] + current['Low'])/2 and current['High'] > prev['High']
  df.loc[idx,'Inside Bar'] = current['High'] < prev['High'] and current['Low'] > prev['Low']
  df.loc[idx,'Outside Bar'] = current['High'] > prev['High'] and current['Low'] < prev['Low']
  df.loc[idx,'Bullish Engulfing'] = current['High'] > prev['High'] and current['Low'] < prev['Low'] and realbody >= 0.8 * candle_range and current['Close'] > current['Open']
  df.loc[idx,'Bearish Engulfing'] = current['High'] > prev['High'] and current['Low'] < prev['Low'] and realbody >= 0.8 * candle_range and current['Close'] < current['Open']

df.fillna(False, inplace=True)
df = df.drop(columns = ['Stock Splits', 'Dividends', 'Volume', 'Open', 'High', 'Low'])
print(df.tail(10))