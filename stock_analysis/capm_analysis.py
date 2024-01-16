from pandas_datareader import data as pdr
import numpy as np
import pandas as pd
import datetime
from socket import gaierror
from pandas_datareader._utils import RemoteDataError
import tickers as ti

# Fetches stock data for a given ticker.
def get_stock_data(ticker, start, end):
    return pdr.DataReader(ticker, 'yahoo', start, end)

# Calculates expected return using CAPM.
def calculate_expected_return(stock, index, risk_free_return):
    # Resample to monthly data
    return_stock = stock.resample('M').last()['Adj Close']
    return_index = index.resample('M').last()['Adj Close']

    # Create DataFrame with returns
    df = pd.DataFrame({'stock_close': return_stock, 'index_close': return_index})
    df[['stock_return', 'index_return']] = np.log(df / df.shift(1))
    df = df.dropna()

    # Calculate beta and alpha
    beta, alpha = np.polyfit(df['index_return'], df['stock_return'], deg=1)
    
    # Calculate expected return
    expected_return = risk_free_return + beta * (df['index_return'].mean() * 12 - risk_free_return)
    return expected_return

def main():
    # Risk-free return rate
    risk_free_return = 0.02

    # Define time period
    start = datetime.datetime.now() - datetime.timedelta(days=365)
    end = datetime.date.today()

    # Get all tickers in NASDAQ
    nasdaq_tickers = ti.tickers_nasdaq()

    # Index ticker
    index_ticker = '^GSPC'

    # Fetch index data
    try:
        index_data = get_stock_data(index_ticker, start, end)
    except RemoteDataError:
        print("Failed to fetch index data.")
        return

    # Loop through NASDAQ tickers
    for ticker in nasdaq_tickers:
        try:
            # Fetch stock data
            stock_data = get_stock_data(ticker, start, end)

            # Calculate expected return
            expected_return = calculate_expected_return(stock_data, index_data, risk_free_return)

            # Output expected return
            print(f'{ticker}: Expected Return: {expected_return}')

        except (RemoteDataError, gaierror):
            print(f"Data not available for ticker: {ticker}")

if __name__ == "__main__":
    main()