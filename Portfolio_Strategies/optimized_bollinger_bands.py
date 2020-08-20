import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
import yfinance as yf
import talib as ta
yf.pdr_override()
pd.set_option('display.max_columns', None)

def get_data(sym):
    df = pdr.get_data_yahoo(sym)
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Returns"] = (df["Close"].shift(1) - df["Close"].shift(2)) / df["Close"].shift(2)
    return df

def plot_candles(df, l=0):
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
    plt.show()

def add_momentum(df, lb=20, std=2):
    df["MA"] = df["Returns"].rolling(lb).mean()
    df["STD"] = df["Returns"].rolling(lb).std()
    df["OVB"] = df["Close"].shift(1) * (1 + (df["MA"] + df["STD"] * std))
    df["OVS"] = df["Close"].shift(1) * (1 + (df["MA"] - df["STD"] * std))
    df['SMA'] = ta.SMA(df['Adj Close'], timeperiod = 20)
    return df

def stats(df):
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
# df["Returns"].hist(bins=750, grid=False, figsize=(15,10))

df = add_momentum(df, 20, 3)
plot_candles(df, 150)
print(stats(df))