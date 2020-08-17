import datetime
import talib
from pandas_datareader import DataReader
import numpy as np
import yahoo_fin.stock_info as si

#Get Dates
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

tickers = si.tickers_dow()

oversold = []
overbought = []

for ticker in tickers[:1]:
    for timeperiod in np.arange(5,30, 1):
        try:
            data = DataReader(ticker, 'yahoo', start_date, end_date)
            data["rsi"] = talib.RSI(data["Adj Close"], timeperiod=timeperiod)

            value = data['rsi'][-1]
            print ('\n{} has an rsi value of {}'.format(ticker, round(value, 2)))
        except Exception as e:
            print (e)
            continue
print (oversold)
print (overbought)
