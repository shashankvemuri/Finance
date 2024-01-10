import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

# Override default data reader method with yfinance
yf.pdr_override()

# Define the start and end dates for data retrieval
start = dt.datetime(2019, 1, 1)
now = dt.datetime.now()

# Define the moving averages and exponential moving averages to be used
smaUsed = [50, 200]
emaUsed = [21]

# User inputs for stock ticker and position
stock = input("Enter a ticker: ")
position = input("Buy or Short? ").lower()
AvgGain = float(input("Enter Your Average Gain (%): "))
AvgLoss = float(input("Enter Your Average Loss (%): "))

# Fetch historical data from Yahoo Finance
df = pdr.get_data_yahoo(stock, start, now)

# Calculate the maximum stop value and target returns based on user's position
if position == "buy":
    close = df["Adj Close"][-1]
    maxStop = close * (1 - AvgLoss / 100)
    targets = [round(close * (1 + (i * AvgGain / 100)), 2) for i in range(1, 4)]
elif position == "short":
    close = df["Adj Close"][-1]
    maxStop = close * (1 + AvgLoss / 100)
    targets = [round(close * (1 - (i * AvgGain / 100)), 2) for i in range(1, 4)]

# Calculate SMA and EMA for the stock
for x in smaUsed:
    df[f"SMA_{x}"] = df["Adj Close"].rolling(window=x).mean()
for x in emaUsed:
    df[f"EMA_{x}"] = df["Adj Close"].ewm(span=x, adjust=False).mean()

# Fetching the latest values of SMA, EMA, and 5 day low
sma_values = {f"SMA_{x}": round(df[f"SMA_{x}"][-1], 2) for x in smaUsed}
ema_values = {f"EMA_{x}": round(df[f"EMA_{x}"][-1], 2) for x in emaUsed}
low5 = round(min(df["Low"].tail(5)), 2)

# Calculate the performance metrics and checks
performance_checks = {}
for key, value in {**sma_values, **ema_values, "Low_5": low5}.items():
    pf = round(((close / value) - 1) * 100, 2)
    check = value > maxStop if position == "buy" else value < maxStop
    performance_checks[key] = {"Performance": pf, "Check": check}

# Displaying the results
print(f"\nCurrent Stock: {stock} | Price: {round(close, 2)}")
print(" | ".join([f"{key}: {value}" for key, value in {**sma_values, **ema_values, 'Low_5': low5}.items()]))
print("-------------------------------------------------")
print(f"Max Stop: {round(maxStop, 2)}")
print(f"Price Targets: 1R: {targets[0]} | 2R: {targets[1]} | 3R: {targets[2]}")
for key, value in performance_checks.items():
    print(f"From {key} {value['Performance']}% - {'Within' if value['Check'] else 'Outside'} Max Stop")