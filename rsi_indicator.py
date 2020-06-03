import requests
import datetime
import talib
from pandas_datareader import DataReader
import pickle 
import bs4 as bs 
import time 
import pandas as pd

#Get Dates
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

tickers = pd.read_pickle('spxTickers.pickle')

oversold = []
overbought = []

for ticker in tickers:
    try:
        data = DataReader(ticker, 'yahoo', start_date, end_date)
        data["rsi"] = talib.RSI(data["Close"])
        values = data["rsi"].tail(14)
        value = values.mean()
        print ('{} has an rsi value of {}'.format(ticker, round(value, 2)))
        time.sleep(1)
        
        if value <= 30:
            oversold.append(ticker)
            
        elif value >= 70:
            overbought.append(ticker)
    except Exception as e:
        print (e)
        continue
        
print (oversold)
print (overbought)