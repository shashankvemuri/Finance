from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
yf.pdr_override()

def astral(data, completion, step, step_two, what, high, low, where_long, where_short):
    # Timing buy signal
    counter = -1
    for i in range(len(data)):    
        if data[i, what] < data[i - step, what] and data[i, low] < data[i - step_two, low]:
            data[i, where_long] = counter
            counter += -1       
            if counter == -completion - 1:
                counter = 0
            else:
                continue        
        elif data[i, what] >= data[i - step, what]:
            counter = -1 
            data[i, where_long] = 0 
            
        # Timing sell signal       
        counter = 1 
        
        for i in range(len(data)):
            if data[i, what] > data[i - step, what] and data[i, high] > data[i - step_two, high]: 
                data[i, where_short] = counter 
                counter += 1        
                if counter == completion + 1: 
                    counter = 0            
                else:
                    continue        
            elif data[i, what] <= data[i - step, what]: 
                counter = 1 
                data[i, where_short] = 0 
          
        return data
    
# The completion variable refers to Astral's final count
# The step variable refers to Astral's first lookback
# The step_two variable refers to Astral's second lookback
# The what variable refers to the closing price
# The high variable refers to the high price
# The low variable refers to the low price
# The where_long variable refers to where to put the buy trigger
# The where_short variable refers to where to put the sell trigger

ticker = 'APPS'
start = dt.datetime.today() - dt.timedelta(days=int(365.25*2))
end = dt.datetime.today()
data = pdr.get_data_yahoo(ticker, start, end)

print(astral(data, 8, 1, 5, data['Close'], data['High'], data['Low'], 8, -8))
