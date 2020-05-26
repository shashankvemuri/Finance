from yahoo_fin import stock_info as si
import numpy as np 
from finsymbols import symbols
from pprint import pprint

nasdaq_tickers = si.tickers_nasdaq()
#print (len(nasdaq_tickers))

#print(len(si.tickers_sp500()))

#print(len(si.tickers_dow()))
