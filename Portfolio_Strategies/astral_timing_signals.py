# Import dependencies
from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

# Allow pandas_datareader to use Yahoo Finance as a data source
yf.pdr_override()

def astral(data, completion, step, step_two, what, high, low, where_long, where_short):
    """
    Determines timing for buy and sell signals in stock data, based on input parameters.

    Parameters:
    data (pd.DataFrame): The stock data to analyze.
    completion (int): The number of periods to wait before changing the signal.
    step (int): The number of periods to use as the first reference point.
    step_two (int): The number of periods to use as the second reference point.
    what (str): The name of the column in data to use as the comparison.
    high (str): The name of the column in data to use as the high reference point.
    low (str): The name of the column in data to use as the low reference point.
    where_long (str): The name of the column in data to use for long signals.
    where_short (str): The name of the column in data to use for short signals.

    Returns:
    pd.DataFrame: The modified data with long and short signals added.
    """
    counter = -1  # Initialize the counter for long signals
    for i in range(len(data)):    
        if data[i, what] < data[i - step, what] and data[i, low] < data[i - step_two, low]:
            # If a long signal is triggered, set the signal value and decrement the counter
            data[i, where_long] = counter
            counter += -1       
            if counter == -completion - 1:
                counter = 0
            else:
                continue        
        elif data[i, what] >= data[i - step, what]:
            # If the current value is greater than or equal to the first reference point, reset the counter and signal value
            counter = -1 
            data[i, where_long] = 0 
            
        counter = 1  # Initialize the counter for short signals
        
        for i in range(len(data)):
            if data[i, what] > data[i - step, what] and data[i, high] > data[i - step_two, high]: 
                # If a short signal is triggered, set the signal value and increment the counter
                data[i, where_short] = counter 
                counter += 1        
                if counter == completion + 1: 
                    counter = 0            
                else:
                    continue        
            elif data[i, what] <= data[i - step, what]: 
                # If the current value is less than or equal to the first reference point, reset the counter and signal value
                counter = 1 
                data[i, where_short] = 0 
          
        return data

# Set the ticker and date range for the stock data to analyze
ticker = 'APPS'
start = dt.datetime.today() - dt.timedelta(days=int(365.25*2))
end = dt.datetime.today()
data = pdr.get_data_yahoo(ticker, start, end)

# Print the modified data with long and short signals added
print(astral(data, 8, 1, 5, data['Close'], data['High'], data['Low'], 'long_signal', 'short_signal'))