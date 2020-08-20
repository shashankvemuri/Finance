import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
import yfinance as yf
yf.pdr_override()

def get_data(sym):
    df = pdr.get_data_yahoo(sym)
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    # we need to shift or we will have lookahead bias in code
    df["Returns"] = (df["Close"].shift(1) - df["Close"].shift(2)) / df["Close"].shift(2)
    return df

def plot_candles(df, l=0):
    db = df.copy()
    if l > 0:
        db = db[-l:]
    db = db.reset_index(drop=True).reset_index()
    db["Up"] = db["Close"] > db["Open"]
    db["Bottom"] = np.where(db["Up"], db["Open"], db["Close"])
    db["Bar"] = db["High"] - db["Low"]
    db["Body"] = abs(db["Close"] - db["Open"])
    db["Color"] = np.where(db["Up"], "g", "r")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    plt.title(f'{sym} Optimized Bollinger Bands')
    plt.ylabel('Price')
    plt.xlabel('Dates')
    ax.bar(db["index"], bottom=db["Low"], height=db["Bar"], width=0.25, color="#000000")
    ax.bar(db["index"], bottom=db["Bottom"], height=db["Body"], width=0.5, color=db["Color"])
    ax.plot(db["OVB"], color="r", linewidth=.25)
    ax.plot(db["OVS"], color="r", linewidth=.25)
    plt.show()

def add_momentum(df, lb=20, std=2):
    df["MA"] = df["Returns"].rolling(lb).mean()
    df["STD"] = df["Returns"].rolling(lb).std()
    df["OVB"] = df["Close"].shift(1) * (1 + (df["MA"] + df["STD"] * std))
    df["OVS"] = df["Close"].shift(1) * (1 + (df["MA"] - df["STD"] * std))
    return df

def stats(df):
    total = len(df)
    ins1 = df[(df["Close"] > df["OVS"]) & (df["Close"] < df["OVB"])]
    ins2 = df[(df["Close"] > df["OVS"])]
    ins3 = df[(df["Close"] < df["OVB"])]
    il1 = len(ins1)
    il2 = len(ins2)
    il3 = len(ins3)
    r1 = np.round(il1 / total * 100, 2)
    r2 = np.round(il2 / total * 100, 2)
    r3 = np.round(il3 / total * 100, 2)
    return r1, r2, r3

sym = input('Enter a ticker: ')
df = get_data(sym)
df["Returns"].hist(bins=750, grid=False, figsize=(15,10))

df = add_momentum(df, 20, 2)
plot_candles(df, 100)
print(stats(df))