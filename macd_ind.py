from pylab import rcParams
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import datetime as dt

ticker = 'AAPL'
num_of_years = 2
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.datetime.now() 

df = DataReader(ticker, 'yahoo', start, now)['Close']
df = df.reset_index()
df.columns=['ds','y']

exp1 = df.y.ewm(span=12, adjust=False).mean()
exp2 = df.y.ewm(span=26, adjust=False).mean()
macd = exp1-exp2
exp3 = macd.ewm(span=9, adjust=False).mean()
rcParams['figure.figsize'] = 15,10
plt.plot(df.ds, macd, label=f'{ticker} MACD', color = '#EBD2BE')
plt.plot(df.ds, exp3, label='Signal Line', color='#E5A4CB')
plt.legend(loc='upper left')
plt.subplots()
plt.show()

exp1 = df.y.ewm(span=12, adjust=False).mean()
exp2 = df.y.ewm(span=26, adjust=False).mean()
exp3 = df.y.ewm(span=9, adjust=False).mean()
macd = exp1-exp2
rcParams['figure.figsize'] = 15,10
plt.plot(df.ds, df.y, label=f'{ticker}')
plt.plot(df.ds, macd, label=f'{ticker} MACD', color='orange')
plt.plot(df.ds, exp3, label='Signal Line', color='Magenta')
plt.legend(loc='upper left')
plt.show()