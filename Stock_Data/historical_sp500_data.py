import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt
import pandas as pd
import yahoo_fin.stock_info as si

yf.pdr_override()

tickers = si.tickers_sp500()
tickers = [item.replace('.', '-') for item in tickers]

num_of_years = 10
start = dt.date.today() - dt.timedelta(days = int(365.25*num_of_years))

for ticker in tickers:
    try:
        df = pdr.get_data_yahoo(ticker, start)
        df.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/S&P500/{ticker}.csv')
        print (f'{ticker} is done')
    except:
        continue