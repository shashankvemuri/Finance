# Imports
from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
import datetime
import time
import sys
import os
yf.pdr_override()
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import tickers as ti

# Setting up variables
tickers = ti.tickers_sp500()
tickers = [ticker.replace(".", "-") for ticker in tickers]
index_name = '^GSPC'
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()
exportList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])

# Fetching S&P 500 index data
index_df = pdr.get_data_yahoo(index_name, start_date, end_date)
index_df['Percent Change'] = index_df['Adj Close'].pct_change()
index_return = index_df['Percent Change'].cumprod().iloc[-1]

# Identifying top performing stocks
returns_multiples = []
for ticker in tickers:
    # Download stock data
    df = pdr.get_data_yahoo(ticker, start_date, end_date)
    df['Percent Change'] = df['Adj Close'].pct_change()
    stock_return = df['Percent Change'].cumprod().iloc[-1]
    returns_multiple = round(stock_return / index_return, 2)
    returns_multiples.append(returns_multiple)
    time.sleep(1)

# Creating a DataFrame for top 30% stocks
rs_df = pd.DataFrame({'Ticker': tickers, 'Returns_multiple': returns_multiples})
rs_df['RS_Rating'] = rs_df['Returns_multiple'].rank(pct=True) * 100
top_stocks = rs_df[rs_df['RS_Rating'] >= rs_df['RS_Rating'].quantile(0.70)]['Ticker']

# Applying Minervini's criteria
for stock in top_stocks:
    try:
        df = pd.read_csv(f'{stock}.csv', index_col=0)
        df['SMA_50'] = df['Adj Close'].rolling(window=50).mean()
        df['SMA_150'] = df['Adj Close'].rolling(window=150).mean()
        df['SMA_200'] = df['Adj Close'].rolling(window=200).mean()
        current_close = df['Adj Close'].iloc[-1]
        low_52_week = df['Low'].rolling(window=260).min().iloc[-1]
        high_52_week = df['High'].rolling(window=260).max().iloc[-1]
        rs_rating = rs_df[rs_df['Ticker'] == stock]['RS_Rating'].iloc[0]

        # Minervini conditions
        conditions = [
            current_close > df['SMA_150'].iloc[-1] > df['SMA_200'].iloc[-1],
            df['SMA_150'].iloc[-1] > df['SMA_200'].iloc[-20],
            current_close > df['SMA_50'].iloc[-1],
            current_close >= 1.3 * low_52_week,
            current_close >= 0.75 * high_52_week
        ]

        if all(conditions):
            exportList = exportList.append({
                'Stock': stock, 
                "RS_Rating": rs_rating,
                "50 Day MA": df['SMA_50'].iloc[-1], 
                "150 Day Ma": df['SMA_150'].iloc[-1], 
                "200 Day MA": df['SMA_200'].iloc[-1], 
                "52 Week Low": low_52_week, 
                "52 week High": high_52_week
            }, ignore_index=True)

    except Exception as e:
        print(f"Could not gather data on {stock}: {e}")

# Exporting the results
exportList.sort_values(by='RS_Rating', ascending=False, inplace=True)
print(exportList)
exportList.to_csv("ScreenOutput.csv")