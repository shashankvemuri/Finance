import matplotlib.pyplot as plt
from pylab import rcParams
import yfinance as yf
import datetime as dt
import warnings
import talib 
import ta
from statistics import mean
import pandas as pd
import time
from yahoo_fin import stock_info as si

warnings.filterwarnings("ignore")
yf.pdr_override()
pd.set_option('display.max_columns', None)

num_of_years = 1
start = dt.date.today() - dt.timedelta(days = int(365.25 * num_of_years))
end = dt.date.today()

tickers = si.tickers_sp500()
tickers = [item.replace(".", "-") for item in tickers]

frames = []
for symbol in tickers:
    try:
        ticker = ['{}'.format(symbol)]
        
        # Read data 
        data = yf.download(symbol,start,end)
        
        # ## SMA and EMA
        #Simple Moving Average
        data['SMA'] = talib.SMA(data['Adj Close'], timeperiod = 20)
        
        # Exponential Moving Average
        data['EMA'] = talib.EMA(data['Adj Close'], timeperiod = 20)
        
        # Bollinger Bands
        data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['Adj Close'], timeperiod =20)
        
        # ## MACD (Moving Average Convergence Divergence)
        # MACD
        data['macd'], data['macdsignal'], data['macdhist'] = talib.MACD(data['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        # ## RSI (Relative Strength Index)
        # RSI
        data['RSI'] = talib.RSI(data['Adj Close'], timeperiod=14)
        
        # ## OBV (On Balance Volume)
        # OBV
        data['OBV'] = talib.OBV(data['Adj Close'], data['Volume'])/10**6
        
        close = data['Adj Close'].tolist()
        close = close[::-1]
        
        sma = data.SMA.tolist()
        sma = sma[::-1]
        
        ema = data.EMA.tolist()
        ema = ema[::-1]
        
        upper = data.upper_band.tolist()
        upper = upper[::-1]
        
        middle = data.middle_band.tolist()
        middle = middle[::-1]
        
        lower = data.lower_band.tolist()
        lower = lower[::-1]
        
        macd = data.macd.tolist()
        macd = macd[::-1]
        
        macd_signal = data.macdsignal.tolist()
        macd_signal = macd_signal[::-1]
        
        rsi = data.RSI.tolist()
        rsi = rsi[::-1]
        
        obv_diff = data['OBV'].diff().tolist()
        obv_diff = obv_diff[::-1]
        obv_diff = mean(obv_diff[:14])
        
        cci = ta.trend.cci(data['High'], data['Low'], data['Close'], n=31, c=0.015)
        # moving averages
        if ema[0] > sma[0]:
            signal_1 = 0
        else: 
            signal_1 = 5
            
        # bollinger bands
        if close[0] > upper[0]:
            signal_2 = 5
        elif close[0] < lower[0]: 
            signal_2 = 0
        else:
            signal_2 = 3
            
        # macd
        if macd[0] > macd_signal[0]:
            signal_3 = 0
        else: 
            signal_3 = 5
            
        # rsi
        if rsi[0] < 30:
            signal_4 = 0
        elif rsi[0] > 70: 
            signal_4 = 5
        else:
            signal_4 = 3
            
        # obv
        if obv_diff > 0:
            signal_5 = 0
        else: 
            signal_5 = 5
        
        # cci
        if cci.tolist()[-1] > 0:
            signal_6 = 0
        else: 
            signal_6 = 5
            
        overall_signal = [round((signal_1 + signal_2 + signal_3 + signal_4 + signal_5 + signal_6)/6), 2]
        smas = [round(sma[0], 2)]
        emas = [round(ema[0], 2)]
        closes = [round(close[0], 2)]
        uppers = [round(upper[0], 2)]
        lowers = [round(lower[0], 2)]
        macds = [round(macd[0], 2)]
        macd_signals = [round(macd_signal[0], 2)]
        rsis = [round(rsi[0], 2)]
        obvs = [round(obv_diff, 2)]
        ccis = [round(cci.tolist()[-1], 2)]
        
        dataframe = pd.DataFrame(list(zip(ticker, overall_signal, smas, emas, closes, uppers, lowers, macds, macd_signals, rsis, obvs, ccis)), columns =['Company', 'Signal', 'SMA', 'EMA', 'Adj Close', 'Upper Band', 'Lower Band', 'MACD', 'MACD Signal' ,'Relative Strength Index', 'On Balance Volume', 'Commodity Channel Index'])
        dataframe = dataframe.set_index('Company')
        frames.append(dataframe)
        
        dataframe = dataframe.transpose()
        print (dataframe)
        
        time.sleep(1)
    except Exception as e:
        continue

df = pd.concat(frames)
df.to_csv('../Outputs/indicator_signals/indicator_signals.csv')
print (df)
