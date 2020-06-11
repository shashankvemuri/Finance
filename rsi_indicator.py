import requests
import datetime
import talib
from pandas_datareader import DataReader
import pickle 
import bs4 as bs 
import time 
import pandas as pd
from tqdm import tqdm

#Get Dates
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

tickers = pd.read_pickle('spxTickers.pickle')

oversold = []
overbought = []

with tqdm(total=len(tickers), desc="RSI Indicator", bar_format="{l_bar}{bar} [ time left: {remaining} ]") as pbar:
    for ticker in tickers:
        try:
            data = DataReader(ticker, 'yahoo', start_date, end_date)
            data["rsi"] = talib.RSI(data["Close"])
            values = data["rsi"].tail(14)
            value = values.mean()
            print ('\n{} has an rsi value of {}'.format(ticker, round(value, 2)))
            time.sleep(1)
            
            if value <= 30:
                oversold.append(ticker)
                
            elif value >= 70:
                overbought.append(ticker)

        except Exception as e:
            print (e)
            continue
        
        pbar.update(1)
        print ('\n')
        print ('-'*50)

print (oversold)
print (overbought)