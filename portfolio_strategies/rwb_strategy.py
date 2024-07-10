import datetime as dt
import yfinance as yf
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import numpy as np

yf.pdr_override()

emas_used = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

def get_stock_data(ticker, num_of_years):
    start_date = dt.date.today() - dt.timedelta(days=365.25 * num_of_years)
    end_date = dt.datetime.now()
    df = pdr.get_data_yahoo(ticker, start_date, end_date).dropna()
    for ema in emas_used:
        df[f"Ema_{ema}"] = df.iloc[:, 4].ewm(span=ema, adjust=False).mean()
    return df.iloc[60:]

def rwb_strategy(df):
    pos, num, percent_change = 0, 0, []
    for i in df.index:
        cmin = min(df[f"Ema_{ema}"][i] for ema in emas_used[:6])
        cmax = max(df[f"Ema_{ema}"][i] for ema in emas_used[6:])
        close = df["Adj Close"][i]
        if cmin > cmax and pos == 0:
            bp, pos = close, 1
            print(f"Buying now at {bp}")
        elif cmin < cmax and pos == 1:
            pos, sp = 0, close
            print(f"Selling now at {sp}")
            percent_change.append((sp / bp - 1) * 100)
        if num == df["Adj Close"].count() - 1 and pos == 1:
            pos, sp = 0, close
            print(f"Selling now at {sp}")
            percent_change.append((sp / bp - 1) * 100)
        num += 1
    return percent_change

stock = input("Enter a ticker: ")
num_of_years = float(input("Enter number of years: "))
df = get_stock_data(stock, num_of_years)
percent_change = rwb_strategy(df)

gains = sum(i for i in percent_change if i > 0)
losses = sum(i for i in percent_change if i < 0)
total_trades = len(percent_change)
total_return = round((np.prod([1 + i/100 for i in percent_change]) - 1) * 100, 2)

print(f"Results for {stock.upper()} going back to {num_of_years} years:")
print(f"Number of Trades: {total_trades}")
print(f"Total return: {total_return}%")

plt.figure(figsize=(15, 10))
for ema in emas_used:
    plt.plot(df[f"Ema_{ema}"], label=f"Ema_{ema}")
plt.plot(df["Adj Close"], color="g", label="Adj Close")
plt.title(f"RWB Strategy for {stock.upper()}")
plt.ylabel("Price")
plt.xlabel("Date")
plt.legend()
plt.show()