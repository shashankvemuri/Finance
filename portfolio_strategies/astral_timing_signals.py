# Importing necessary libraries
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# Allow pandas_datareader to use Yahoo Finance as a data source
yf.pdr_override()

# Apply Astral Timing signals to stock data.
def astral(data, completion, step, step_two, what, high, low, where_long, where_short):
    data['long_signal'] = 0
    data['short_signal'] = 0

    # Iterate through the DataFrame
    for i in range(len(data)):
        # Long signal logic
        if data.iloc[i][what] < data.iloc[i - step][what] and data.iloc[i][low] < data.iloc[i - step_two][low]:
            data.at[data.index[i], 'long_signal'] = -1
        elif data.iloc[i][what] >= data.iloc[i - step][what]:
            data.at[data.index[i], 'long_signal'] = 0

        # Short signal logic
        if data.iloc[i][what] > data.iloc[i - step][what] and data.iloc[i][high] > data.iloc[i - step_two][high]:
            data.at[data.index[i], 'short_signal'] = 1
        elif data.iloc[i][what] <= data.iloc[i - step][what]:
            data.at[data.index[i], 'short_signal'] = 0

    return data

# Define stock ticker and date range
ticker = 'APPS'
start = dt.datetime.today() - dt.timedelta(days=365.25 * 2)
end = dt.datetime.today()

# Fetch stock data
data = pdr.get_data_yahoo(ticker, start, end)

# Apply Astral Timing signals
astral_data = astral(data, 8, 1, 5, 'Close', 'High', 'Low', 'long_signal', 'short_signal')

# Display the results
print(astral_data[['long_signal', 'short_signal']])