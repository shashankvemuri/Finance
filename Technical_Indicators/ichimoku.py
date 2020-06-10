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
df = yf.download(symbol,start,end)

# First Create Tenkan_Sen
high_9 = df['High'].rolling(9).max()
low_9 = df['Low'].rolling(9).min()
df['Tenkan_Sen'] = (high_9 + low_9) /2

# Second Create Kijun Sen
high_26 = df['High'].rolling(26).max()
low_26 = df['Low'].rolling(26).min()
df['Kijun_Sen'] = (high_26 + low_26) /2

# Third Create Senkou Span A 
df['Senkou_Span_A'] = ((df['Tenkan_Sen'] + df['Kijun_Sen']) / 2).shift(26)

# Fourth Create Senkou Span B 
high_52 = df['High'].rolling(52).max()
low_52 = df['Low'].rolling(52).min()
df['Senkou_Span_B'] = ((high_52 + low_52) /2).shift(26)

df['Chikou_Span'] = df['Adj Close'].shift(-26)

plt.figure(figsize=(18,12))
plt.plot(df['Adj Close'], '-b')
plt.plot(df['Kijun_Sen'],  'b--')
plt.plot(df['Tenkan_Sen'],  'r--')
plt.plot(df['Chikou_Span'], 'g--')
plt.plot(df['Senkou_Span_A'], 'r')
plt.plot(df['Senkou_Span_B'], 'g')
plt.fill_between(df.index, df['Senkou_Span_A'], df['Senkou_Span_B'], where=df['Senkou_Span_A']> df['Senkou_Span_B'], facecolor='blue', interpolate=True, alpha=0.25)
plt.fill_between(df.index, df['Senkou_Span_A'], df['Senkou_Span_B'], where=df['Senkou_Span_B']> df['Senkou_Span_A'], facecolor='crimson', interpolate=True, alpha=0.25)
plt.grid()
plt.legend(loc='best')
plt.title('Stock for Ichimoku Kinko Hyo')
plt.show()


df2 = df.reset_index()
df2 = df2.apply(pd.to_numeric, errors='ignore')

# This one does not show dates
plt.figure(figsize=(18,12))
plt.plot(df2['Date'], df2['Adj Close'], '-b')
plt.plot(df2['Date'], df2['Kijun_Sen'],  'b--')
plt.plot(df2['Date'], df2['Tenkan_Sen'],  'r--')
plt.plot(df2['Date'], df2['Chikou_Span'], 'g--')
plt.plot(df2['Date'], df2['Senkou_Span_A'], 'r')
plt.plot(df2['Date'], df2['Senkou_Span_B'], 'g')
plt.fill_between(df2['Date'], df2['Senkou_Span_A'], df2['Senkou_Span_B'], where=df2['Senkou_Span_A']> df2['Senkou_Span_B'], facecolor='blue', interpolate=True, alpha=0.25)
plt.fill_between(df2['Date'], df2['Senkou_Span_A'], df2['Senkou_Span_B'], where=df2['Senkou_Span_B']> df2['Senkou_Span_A'], facecolor='crimson', interpolate=True, alpha=0.25)
plt.legend(loc='best')
plt.title('Stock for Ichimoku Kinko Hyo')
plt.show()