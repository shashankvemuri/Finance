import pandas as pd
import numpy as np
import datetime as dt
import pandas_datareader.data as pdr
import yfinance as yf
yf.pdr_override()
import pandas as pd
import numpy as np

def SMA(data, timeperiod=14):
    """
    Simple Moving Average (SMA).
    Calculates the average of a selected range of prices, usually closing prices, 
    by the number of periods in that range.
    """
    return data.rolling(window=timeperiod).mean()

def EMA(data, timeperiod=12):
    """
    Exponential Moving Average (EMA).
    Unlike the Simple Moving Average (SMA) which assigns equal weight to all values, the EMA provides 
    a higher weight to recent prices.
    """
    ema = data.ewm(span=timeperiod, adjust=False).mean()
    return ema

def WMA(values, n):
    """
    Weighted Moving Average (WMA).
    Similar to the EMA, the WMA assigns more weight to recent data points. The difference lies in 
    the method of weight assignment, which is linear in the case of WMA.
    """
    return values.ewm(alpha=1/n, adjust=False).mean()

def ATR(high, low, close, timeperiod=14):
    """
    Average True Range (ATR).
    An indicator that measures market volatility by decomposing the entire range of an asset for 
    a given period.
    """
    data = pd.DataFrame()
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = WMA(tr, timeperiod)
    return atr

def BBANDS(data, timeperiod=20, nbdevup=2, nbdevdn=2, matype=None):
    """
    Bollinger Bands (BBANDS).
    Consists of an upper and a lower band which are dynamic levels that adjust themselves 
    as the market moves - used to measure the market’s volatility. 
    """
    sma = data.rolling(timeperiod).mean()
    std = data.rolling(timeperiod).std()
    bollinger_up = sma + std * nbdevup
    bollinger_down = sma - std * nbdevdn
    return bollinger_up, sma, bollinger_down

def STOCH(high, low, close, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    """
    Stochastic Oscillator (STOCH).
    A momentum indicator comparing the closing price of a security to the range of its prices 
    over a certain period of time.
    """
    high = high.rolling(fastk_period).max()
    low = low.rolling(fastk_period).min()

    fastk = ((close - low) / (high - low)) * 100
    fastd = fastk.rolling(slowk_period).mean()
    slowk = fastd.rolling(slowk_period).mean()

    if slowd_matype == 0:
        slowd = slowk.rolling(slowd_period).mean()
    else:
        slowd = slowk.rolling(slowd_period).apply(lambda x: np.convolve(x, np.ones(slowd_period), mode='valid') / slowd_period)

    return slowk, slowd

def RSI(data, timeperiod=14):
    """
    Relative Strength Index (RSI).
    A momentum oscillator that measures the speed and change of price movements.
    """
    delta = data.diff()
    delta = delta[1:]

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=timeperiod).mean()
    avg_loss = loss.rolling(window=timeperiod).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def CCI(high, low, close, timeperiod=14):
    """
    Commodity Channel Index (CCI).
    An oscillator used to compare the current price to an average price over a period of time - 
    helps determine when an investment vehicle has been overbought and oversold.
    """
    typical_price = (high + low + close) / 3
    sma = typical_price.rolling(timeperiod).mean()
    mean_deviation = np.abs(typical_price - sma).rolling(timeperiod).mean()
    cci = (typical_price - sma) / (0.015 * mean_deviation)
    return cci

def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Moving Average Convergence Divergence (MACD).
    A trend-following momentum indicator that shows the relationship between two moving averages 
    of a security’s price.
    """
    exp1 = data.ewm(span=fastperiod, adjust=False).mean()
    exp2 = data.ewm(span=slowperiod, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signalperiod, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram


def WILLR(high, low, close, timeperiod=14):
    """
    Williams %R.
    Measures the level of the close relative to the high-low range over a given period of time.
    """
    highest_high = high.rolling(window=timeperiod).max()
    lowest_low = low.rolling(window=timeperiod).min()
    willr = -100 * ((highest_high - close) / (highest_high - lowest_low))
    return willr

def OBV(close, volume):
    """
    On Balance Volume (OBV).
    Uses volume flow to predict changes in stock price.
    """
    df = pd.DataFrame({'close': close, 'volume': volume})
    df['obv'] = np.where(df['close'] > df['close'].shift(1), df['volume'], 
                         np.where(df['close'] < df['close'].shift(1), -df['volume'], 0)).cumsum()
    return df['obv']

def AD(high, low, close, volume):
    """
    Chaikin A/D Line.
    A volume-based indicator designed to measure the cumulative flow of money into and out of a security.
    """
    clv = ((close - low) - (high - close)) / (high - low)
    clv.fillna(0, inplace=True)  # Replace NaN values with 0
    ad = clv * volume
    ad = ad.cumsum()
    return ad

def ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10):
    """
    Chaikin A/D Oscillator.
    Similar to the A/D Line but with the addition of a moving average component.
    """
    ad = AD(high, low, close, volume)
    adosc = ad.ewm(span=fastperiod).mean() - ad.ewm(span=slowperiod).mean()
    return adosc

def MFI(high, low, close, volume, timeperiod=14):
    """
    Money Flow Index (MFI).
    A momentum indicator that incorporates both price and volume data, often used to identify overbought 
    or oversold conditions in an asset.
    """
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume
    money_flow_ratio = (
        raw_money_flow.rolling(window=timeperiod).apply(lambda x: np.sum(x[x > x.shift(1)])) / 
        raw_money_flow.rolling(window=timeperiod).apply(lambda x: np.sum(x[x < x.shift(1)]))
    )
    mfi = 100 - (100 / (1 + money_flow_ratio))
    return mfi

def ADX(high, low, close, timeperiod=14):
    """
    Average Directional Index (ADX).
    A trend strength indicator that measures the strength of a trend in a financial instrument. 
    """
    tr = TRANGE(high, low, close)
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr_smooth = tr.rolling(window=timeperiod).sum()
    plus_dm_smooth = plus_dm.rolling(window=timeperiod).sum()
    minus_dm_smooth = minus_dm.abs().rolling(window=timeperiod).sum()

    plus_di = 100 * (plus_dm_smooth / tr_smooth)
    minus_di = 100 * (minus_dm_smooth / tr_smooth)

    dx = 100 * np.abs((plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window=timeperiod).mean()

    return adx

def ATR(high, low, close, timeperiod=14):
    """
    Average True Range (ATR).
    Measures market volatility by decomposing the entire range of an asset price for that period.
    """
    tr = TRANGE(high, low, close)
    atr = tr.rolling(window=timeperiod).mean()
    return atr

def NATR(high, low, close, timeperiod=14):
    """
    Normalized Average True Range (NATR).
    Provides the ATR value relative to the close, allowing comparison between different price levels.
    """
    atr = ATR(high, low, close, timeperiod)
    natr = 100 * (atr / close)
    return natr

def BETA(datax, datay, timeperiod=5):
    """
    Beta.
    Measures the covariance of a stock in relation to the overall market.
    """
    covariance = datax.rolling(window=timeperiod).cov(datay)
    variance = datay.rolling(window=timeperiod).var()
    beta = covariance / variance
    return beta

def STDDEV(data, timeperiod=5, nbdev=1):
    """
    Standard Deviation (STDDEV).
    Measures the market volatility by depicting how much the stock price diverges from its true value.
    """
    return data.rolling(window=timeperiod).std(ddof=0) * nbdev

def TRANGE(high, low, close):
    """
    True Range.
    The greatest of the following: current high minus the current low, the absolute value of the current high 
    minus the previous close, and the absolute value of the current low minus the previous close.
    """
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    true_range = np.maximum(high_low, high_close, low_close)
    return true_range

def MOM(close, timeperiod=10):
    """
    Momentum (MOM).
    Measures the rate of change in a security's price. 
    """
    return close.diff(periods=timeperiod)

def ROC(close, timeperiod=10):
    """
    Rate of Change (ROC).
    Measures the percentage change in price from one period to the next.
    """
    roc = ((close - close.shift(periods=timeperiod)) / close.shift(periods=timeperiod)) * 100
    return roc

def AVGPRICE(open, high, low, close):
    """
    Average Price.
    Calculates the average of the open, high, low, and close prices for each period.
    """
    return (open + high + low + close) / 4

def LINEARREG(close, timeperiod=14):
    """
    Linear Regression.
    A statistical way to predict future prices based on past prices.
    """
    idx = np.arange(timeperiod)
    def linreg(x):
        return np.polyval(np.polyfit(idx, x, 1), idx)[-1]
    return close.rolling(window=timeperiod).apply(linreg, raw=True)

# Mathematical Operators
def ADD(data1, data2):
    """
    Vector Arithmetic Add.
    Adds two data series together.
    """
    return data1 + data2

def DIV(data1, data2):
    """
    Vector Arithmetic Div.
    Divides one data series by another.
    """
    return data1 / data2

def MAX(data, timeperiod=14):
    """
    Highest value over a specified period.
    """
    return data.rolling(window=timeperiod).max()

def MAXINDEX(data, timeperiod=14):
    """
    Index of highest value over a specified period.
    """
    return data.rolling(window=timeperiod).apply(np.argmax) + 1

def MIN(data, timeperiod=14):
    """
    Lowest value over a specified period.
    """
    return data.rolling(window=timeperiod).min()

def MININDEX(data, timeperiod=14):
    """
    Index of lowest value over a specified period.
    """
    return data.rolling(window=timeperiod).apply(np.argmin) + 1

def MINMAX(data, timeperiod=14):
    """
    Lowest and highest values over a specified period.
    """
    min_val = data.rolling(window=timeperiod).min()
    max_val = data.rolling(window=timeperiod).max()
    return min_val, max_val

def MINMAXINDEX(data, timeperiod=14):
    """
    Indexes of lowest and highest values over a specified period.
    """
    min_idx = data.rolling(window=timeperiod).apply(np.argmin) + 1
    max_idx = data.rolling(window=timeperiod).apply(np.argmax) + 1
    return min_idx, max_idx

def MULT(data1, data2):
    """
    Vector Arithmetic Mult.
    Multiplies two data series together.
    """
    return data1 * data2

def SUB(data1, data2):
    """
    Vector Arithmetic Subtraction.
    Subtracts one data series from another.
    """
    return data1 - data2

def SUM(data, timeperiod=14):
    """
    Summation.
    Calculates the sum over a given period.
    """
    return data.rolling(window=timeperiod).sum()