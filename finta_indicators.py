import pandas_datareader as pdr
import datetime
from finta import TA
import pandas as pd
from pylab import rcParams
import matplotlib.pyplot as plt

start = datetime.datetime.now() - datetime.timedelta(days=180)
end = datetime.date.today()
show_price = True

stock = 'AAPL'
indicators = ['BBANDS']

stock = stock.upper()
indicators = [x.upper() for x in indicators]

data = pdr.DataReader(stock, 'yahoo', start, end)

opens = data.Open.tolist()
highs = data.High.tolist()
lows = data.Low.tolist()
closes = data.Close.tolist()
volumes = data.Volume.tolist() 

ohlc = pd.DataFrame(list(zip(opens, highs, lows, closes, volumes)), columns = ["open", "high", "low", "close", "volume"], index=data.index)

if show_price == True:
    plt.plot(ohlc.close)
    plt.plot(TA.BBANDS(ohlc))
    indicators.insert(0, 'Close Price')
    plt.legend(labels = [x for x in indicators], loc="best")
    plt.title(f'{stock} Indicators')
    plt.xlabel('Dates')
    plt.ylabel('Value')
    rcParams['figure.figsize'] = 15, 10
else:
    plt.plot(TA.BBANDS(ohlc))
    plt.legend(labels = [x for x in indicators], loc="best")
    plt.title(f'{stock} Indicators')
    plt.xlabel('Dates')
    plt.ylabel('Value')
    rcParams['figure.figsize'] = 15, 10
plt.show()
