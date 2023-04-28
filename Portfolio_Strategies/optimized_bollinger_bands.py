# Import dependencies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
import yfinance as yf
import talib as ta

yf.pdr_override() # Override pandas_datareader's default Yahoo API with yfinance
pd.set_option('display.max_columns', None) # Display all columns in pandas DataFrame

def get_data(sym):
    """Retrieves historical stock data for a given ticker symbol from Yahoo Finance API."""
    df = pdr.get_data_yahoo(sym)
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    # Calculate daily returns for the stock
    df["Returns"] = (df["Close"].shift(1) - df["Close"].shift(2)) / df["Close"].shift(2)
    return df

def plot_candles(df, l=0):
    """
    Plots a candlestick chart with optimized Bollinger Bands for a given DataFrame of stock data.
    The chart displays the stock's adjusted close price, Bollinger Bands, and buy/sell signals.
    """
    db = df.copy()
    if l > 0:
        db = db[-l:]
    db = db.set_index('Date')
    db["Up"] = db["Close"] > db["Open"]
    db["Bottom"] = np.where(db["Up"], db["Open"], db["Close"])
    db["Bar"] = db["High"] - db["Low"]
    db["Body"] = abs(db["Close"] - db["Open"])
    db["Color"] = np.where(db["Up"], "g", "r")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    plt.title(f'{sym} Optimized Bollinger Bands')
    plt.ylabel('Price')
    plt.xlabel('Date')
    ax.plot(db["Adj Close"], color="b", linewidth=.3)
    ax.plot(db['SMA'], color="g", linewidth=.25)
    ax.plot(db["OVB"], color="r", linewidth=.3)
    ax.plot(db["OVS"], color="r", linewidth=.3)
    
    db = db.reset_index()
    # Identify the buy/sell zone
    db['Buy'] = np.where((db['Adj Close'] < db['OVS']), 1, 0)
    db['Sell'] = np.where((db['Adj Close'] > db['OVB']), 1, 0)
    
    # Identify buy/sell signals
    db['Buy_ind'] = np.where((db['Buy'] > db['Buy'].shift(1)), 1, 0)
    db['Sell_ind'] = np.where((db['Sell'] > db['Sell'].shift(1)), 1, 0)
    
    # Plot the buy and sell signals on the graph
    plt.scatter(db.loc[db['Buy_ind'] == 1, 'Date'].values, db.loc[db['Buy_ind'] == 1, 'Adj Close'].values, label='Buy Signal', color='green', s=25, marker="^")
    plt.scatter(db.loc[db['Sell_ind'] == 1, 'Date'].values, db.loc[db['Sell_ind'] == 1, 'Adj Close'].values, label='Sell Signal', color='red', s=25, marker="v")
    plt.legend()
    plt.show()

def add_momentum(df, lb=30, std=2):
    """
    Adds momentum indicators to a given DataFrame of stock data
    """
    df["MA"] = df["Returns"].rolling(lb).mean()
    df["STD"] = df["Returns"].rolling(lb).std()
    df["OVB"] = df["Close"].shift(1) * (1 + (df["MA"] + df["STD"] * std))
    df["OVS"] = df["Close"].shift(1) * (1 + (df["MA"] - df["STD"] * std))
    df['SMA'] = ta.SMA(df['Adj Close'], timeperiod = lb)
    return df

def calculate_buy_sell_zones(df):
    """
    Calculates and returns the percentage of time the closing price of the stock is
    within the buy zone (ins1), above the sell zone (ins2), and below the buy zone (ins3).
    """
    total = len(df)
    ins1 = df[(df["Close"] > df["OVS"]) & (df["Close"] < df["OVB"])]
    ins2 = df[(df["Close"] > df["OVS"])]
    ins3 = df[(df["Close"] < df["OVB"])]
    r1 = np.round(len(ins1) / total * 100, 2)
    r2 = np.round(len(ins2) / total * 100, 2)
    r3 = np.round(len(ins3) / total * 100, 2)
    return r1, r2, r3

sym = input('Enter a ticker: ')
df = get_data(sym)
df = add_momentum(df, 20, 3)
plot_candles(df, 365 * 3)
print(calculate_buy_sell_zones(df))