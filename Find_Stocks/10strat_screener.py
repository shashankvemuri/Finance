# Imports
from pandas_datareader import DataReader
from scipy.stats import zscore
import datetime as dt
import pandas as pd
import warnings
import talib 
import ta

# Settings
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Get today's date
mylist = []
mylist.append(dt.date.today())
today = mylist[0]

stock = input('Enter a ticker: ')
num_of_years = float(input('Enter the number of years: '))

while stock != 'quit':
    try:
        # Set dates
        start = dt.date.today() - dt.timedelta(days = int(365.25 * num_of_years))
        end = dt.date.today()

        df = DataReader(stock, 'yahoo', start,end)    
        
        # Get Index Data
        index = 'SPY'
        spy = DataReader(index, 'yahoo', start,end)
        spy['RSI'] = talib.RSI(spy['Adj Close'], timeperiod=5)
        
        # Technical Indicators
        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['Adj Close'], timeperiod=7)
        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['RSI'] = talib.RSI(df['Adj Close'], timeperiod=5)
        df['Momentum'] = talib.MOM(df['Adj Close'], timeperiod=5)
        df['Z-Score'] = zscore(df['Adj Close'])
        df['SMA'] = talib.SMA(df['Adj Close'], timeperiod = 7)
        df['EMA'] = talib.EMA(df['Adj Close'], timeperiod = 7)
        df['OBV'] = talib.OBV(df['Adj Close'], df['Volume'])/10**6
        df['OBV'] = df['OBV'].diff()
        df['CCI'] = ta.trend.cci(df['High'], df['Low'], df['Adj Close'], n=7, c=0.015)
        
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
        
            if (df['RSI'].iloc[row] < 25 and spy['RSI'].iloc[row] > 25):
                df['rsiPos'].iloc[row] = 1
            elif (df['RSI'].iloc[row] > 75 and spy['RSI'].iloc[row] < 75):
                df['rsiPos'].iloc[row] = -1
            else:
                df['rsiPos'].iloc[row] = 0
                
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
        frame = pd.DataFrame()
        frame['PC'] = df['Adj Close'].pct_change()
        df = df.drop(columns = ['Open', 'High', 'Low', 'Close', 'Adj Close','Volume', 'upper_band', 'lower_band', 'middle_band', 'lower_band', 'macd', 'macdsignal', 'macdhist','RSI', 'Momentum', 'Z-Score', 'SMA', 'EMA', 'OBV', 'CCI'])
        df['pos'] = df.mean(axis=1)
        df['PC'] = frame['PC']
        
        # Output
        dataframe = pd.DataFrame(zip(df.index, df['PC'].tolist(), df['pos'].tolist()), columns = ['Date', 'Percent Change', 'Signal'])
        dataframe = dataframe.set_index("Date")
        dataframe['Percent Change'] = dataframe['Percent Change'].shift(1)
        dataframe = dataframe.dropna()
        dataframe['Accuracy'] = dataframe['Signal'].mul(dataframe['Percent Change']).ge(0)
        accuracy = round(dataframe['Percent Change'].mul(dataframe['Signal']).ge(0).mean(), 2)
        print (f'Accuracy for {stock.upper()}: ' + str(accuracy))
        print (f'Signal for {stock.upper()}: ' + str(df['pos'].tolist()[-1]))

        stock = input('Enter another ticker: ')

    except Exception as e:
        print (e)