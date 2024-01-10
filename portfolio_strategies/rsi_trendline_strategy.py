import datetime
import time
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
from pandas import ExcelWriter
import sys
import os

# Adding path for ta_functions and ticker modules
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import ta_functions as ta
import tickers as ti

# Override the yfinance module
yf.pdr_override()

# Define the date range for data retrieval
num_of_years = 10
start = datetime.datetime.now() - datetime.timedelta(days=365.25 * num_of_years)
end = datetime.datetime.now()

# Load stock symbols
stocklist = ti.tickers_sp500()
stocklist = [stock.replace(".", "-") for stock in stocklist]  # Adjusting ticker format for Yahoo Finance

# Initialize the DataFrame for exporting results
exportList = pd.DataFrame(columns=['Stock', "RSI", "200 Day MA"])

# Process a limited number of stocks for demonstration
for stock in stocklist[:5]:
    time.sleep(1.5)  # To avoid hitting API rate limits
    print(f"\npulling {stock}")

    # Fetch stock data
    df = pdr.get_data_yahoo(stock, start=start, end=end)

    try:
        # Calculate indicators: 200-day MA, RSI
        df["SMA_200"] = df.iloc[:, 4].rolling(window=200).mean()
        df["rsi"] = ta.RSI(df["Close"])
        currentClose, moving_average_200, RSI = df["Adj Close"][-1], df["SMA_200"][-1], df["rsi"].tail(14).mean()
        two_day_rsi_avg = (df.rsi[-1] + df.rsi[-2]) / 2

        # Define entry criteria
        if currentClose > moving_average_200 and two_day_rsi_avg < 33:
            exportList = exportList.append({'Stock': stock, "RSI": RSI, "200 Day MA": moving_average_200}, ignore_index=True)
            print(f"{stock} made the requirements")

    except Exception as e:
        print(e)  # Handling exceptions

# Exporting the list to an Excel file
today = datetime.date.today()
print(exportList)
writer = ExcelWriter(f'Export-Output_{today}.xlsx')
exportList.to_excel(writer, "Sheet1")
writer.save()