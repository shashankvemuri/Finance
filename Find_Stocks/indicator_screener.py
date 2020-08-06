# Imports
from pandas_datareader import DataReader
from yahoo_fin import stock_info as si
from scipy.stats import zscore
from statistics import mean
import datetime as dt
import pandas as pd
import numpy as np
import warnings
import talib 
import time
import ta

# Settings
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set dates
start = dt.date.today() - dt.timedelta(days = int(365.25 * 1))
end = dt.date.today()

# Set tickers
tickers = si.tickers_sp500()
tickers = [item.replace(".", "-") for item in tickers]

# Get today's date
mylist = []
mylist.append(dt.date.today())
today = mylist[0]

# Get Index Data
index = 'SPY'
spy = DataReader(index, 'yahoo', start,end)
spy['RSI'] = talib.RSI(spy['Adj Close'], timeperiod=14)

# Get Signals
valid_tickers = []
signals = []
for symbol in tickers:
    try:
        df = DataReader(symbol, 'yahoo', start,end)
        
        # Technical Indicators
        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['Adj Close'], timeperiod=14)
        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['RSI'] = talib.RSI(df['Adj Close'], timeperiod=14)
        df['Momentum'] = talib.MOM(df['Adj Close'], timeperiod=14)
        df['Z-Score'] = zscore(df['Adj Close'])
        df['SMA'] = talib.SMA(df['Adj Close'], timeperiod = 20)
        df['EMA'] = talib.EMA(df['Adj Close'], timeperiod = 20)
        df['OBV'] = talib.OBV(df['Adj Close'], df['Volume'])/10**6
        df['OBV'] = df['OBV'].diff()
        df['CCI'] = ta.trend.cci(df['High'], df['Low'], df['Adj Close'], n=31, c=0.015)
        
        # Set signal position columns
        df['bbPos'] = None
        df['macdPos'] = None
        df['rsiPos'] = None
        df['spyPos'] = None
        df['zPos'] = None
        df['mPos'] = None
        df['maPos'] = None
        df['obvPos'] = None
        df['cciPos'] = None

        # Calculate Signals
        for row in range(len(df)):
            if (df['Adj Close'].iloc[row] > df['upper_band'].iloc[row]) and (df['Adj Close'].iloc[row-1] < df['upper_band'].iloc[row-1]):
                df['bbPos'].iloc[row] = -1
            elif (df['Adj Close'].iloc[row] < df['lower_band'].iloc[row]) and (df['Adj Close'].iloc[row-1] > df['lower_band'].iloc[row-1]):
                df['bbPos'].iloc[row] = 1
            else:
                df['bbPos'].iloc[row] = 0
                
            if (df['macd'].iloc[row] > df['macdsignal'].iloc[row]):
                df['macdPos'].iloc[row] = 1
            elif (df['macd'].iloc[row] < df['macdsignal'].iloc[row]):
                df['macdPos'].iloc[row] = -1
            else:
                df['macdPos'].iloc[row] = 0
        
            if (df['RSI'].iloc[row] < 30):
                df['rsiPos'].iloc[row] = 1
            elif (df['RSI'].iloc[row] > 70):
                df['rsiPos'].iloc[row] = -1
            else:
                df['rsiPos'].iloc[row] = 0
            
            if (spy['RSI'].iloc[row] < 30):
                df['spyPos'].iloc[row] = 1
            elif (spy['RSI'].iloc[row] > 70):
                df['spyPos'].iloc[row] = -1
            else:
                df['spyPos'].iloc[row] = 0
                
            if (df['Z-Score'].iloc[row] >= -1.5):
                df['zPos'].iloc[row] = 1
            else:
                df['zPos'].iloc[row] = 0
                
            if (df['Momentum'].iloc[row] > -0.2):
                df['mPos'].iloc[row] = 1
            elif (df['Momentum'].iloc[row] < 0.1):
                df['mPos'].iloc[row] = -1
            else:
                df['mPos'].iloc[row] = 0
                
            if (df['EMA'].iloc[row] > df['SMA'].iloc[row]):
                df['maPos'].iloc[row] = 1
            else:
                df['maPos'].iloc[row] = -1
                
            if (df['OBV'].iloc[row] > 0):
                df['obvPos'].iloc[row] = 1
            else:
                df['obvPos'].iloc[row] = -1
                
            if (df['CCI'].iloc[row] > 0):
                df['cciPos'].iloc[row] = 1
            else:
                df['cciPos'].iloc[row] = -1
            
        # Clean up dataframe
        df = df.drop(columns = ['Open', 'High', 'Low', 'Close', 'Adj Close','Volume', 'upper_band', 'lower_band', 'middle_band', 'lower_band', 'macd', 'macdsignal', 'macdhist','RSI', 'Momentum', 'Z-Score', 'SMA', 'EMA', 'OBV', 'CCI'])
        df['pos'] = df.mean(axis=1)
        
        # Output
        print (f'{symbol} done')
        signals.append(round(mean(df['pos'].tolist()[::-1][:14]), 2))
        valid_tickers.append(symbol)
        time.sleep(.5)
    except:
        continue

# Output
dataframe = pd.DataFrame(zip(valid_tickers, signals), columns = ['Tickers', 'Signal'])
dataframe = dataframe.set_index("Tickers")
dataframe.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/indicator_signals/{today}.csv')
dataframe = dataframe.sort_values('Signal', ascending=False)
print(dataframe)

'''
# Imports
from pandas_datareader import DataReader
from yahoo_fin import stock_info as si
from scipy.stats import zscore
from statistics import mean
import datetime as dt
import pandas as pd
import numpy as np
import warnings
import talib 
import time
import ta

# Settings
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set dates
start = dt.date.today() - dt.timedelta(days = int(365.25 * 1))
end = dt.date.today()

dataframe = pd.read_csv(f'/Users/shashank/Documents/Code/Python/Outputs/indicator_signals/{today}.csv', index_col=0)
dataframe = dataframe.sort_values('Signal', ascending=False)
print(dataframe.head(50))
'''