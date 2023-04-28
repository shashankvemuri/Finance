# Import dependencies
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

yf.pdr_override()

# Get user input for stock ticker and number of years to look back
stock = input("Enter a ticker: ")
num_of_years = float(input("Enter number of years: "))

# Set start and end dates for stock data
start_date = dt.date.today() - dt.timedelta(days=int(365.25 * num_of_years))
end_date = dt.datetime.now()

# Retrieve stock data using Yahoo Finance API
df = pdr.get_data_yahoo(stock, start_date, end_date).dropna()

# Compute exponential moving averages
emas_used = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]
for ema in emas_used:
    df[f"Ema_{ema}"] = round(df.iloc[:, 4].ewm(span=ema, adjust=False).mean(), 2)

# Drop initial rows without exponential moving averages
df = df.iloc[60:]

# Initialize variables
pos = 0
num = 0
percent_change = []

# Loop over stock data
for i in df.index:
    # Compute maximum and minimum exponential moving averages
    cmin = min(df[f"Ema_{ema}"][i] for ema in emas_used[:6])
    cmax = max(df[f"Ema_{ema}"][i] for ema in emas_used[6:])

    # Retrieve current stock price
    close = df["Adj Close"][i]

    # Buy if short-term exponential moving averages are greater than long-term exponential moving averages
    if cmin > cmax:
        if pos == 0:
            bp = close
            pos = 1
            print(f"Buying now at {bp}")
    # Sell if short-term exponential moving averages are less than long-term exponential moving averages
    elif cmin < cmax:
        if pos == 1:
            pos = 0
            sp = close
            print(f"Selling now at {sp}")
            pc = (sp / bp - 1) * 100
            percent_change.append(pc)
    # Sell if end of data is reached and still holding stock
    if num == df["Adj Close"].count() - 1 and pos == 1:
        pos = 0
        sp = close
        print(f"Selling now at {sp}")
        pc = (sp / bp - 1) * 100
        percent_change.append(pc)

    num += 1

# Compute various trading statistics
gains = sum(i for i in percent_change if i > 0)
ng = sum(1 for i in percent_change if i > 0)
losses = sum(i for i in percent_change if i < 0)
nl = sum(1 for i in percent_change if i < 0)
total_return = 1

for i in percent_change:
    total_return = total_return * ((i / 100) + 1)

total_return = round((total_return - 1) * 100, 2)

if ng > 0:
    avg_gain = gains / ng
    max_return = max(percent_change)
else:
    avg_gain = 0
    max_return = "undefined"

if nl > 0:
    avg_loss = losses / nl
    max_loss = min(percent_change)
    gain_loss_ratio = -avg_gain / avg_loss
else:
    avgLoss = 0
    max_loss = "undefined"
    ratio = "inf"

if ng > 0 or nl > 0:
    battingAvg = ng / (ng + nl)
else:
    battingAvg = 0

# Calculate Buy and Hold Result
df["PC"] = df["Adj Close"].pct_change()
hold = round(((df['PC'] / 100 + 1).cumprod().iloc[-1] - 1) * 100, 2)

# Print strategy results and statistics
print()
print(f"Results for {stock.upper()} going back to {str(start_date)}: ")
print("Number of Trades: " + str(ng + nl))
print("Batting Avg: " + str(battingAvg))
print("Gain/loss ratio: " + ratio)
print("Average Gain: " + str(avg_gain))
print("Average Loss: " + str(avgLoss))
print("Max Return: " + max_return)
print("Max Loss: " + max_loss)
print("Total return over " + str(ng + nl) + " trades: " + str(total_return) + "%")
print("Total return for a B&H strategy: " + str(hold) + "%")
print()

# Plot RWB Strategy
plt.subplots()
plt.rcParams["figure.figsize"] = (15, 10)
df = df.tail(252 * 5)
plt.plot(df["Adj Close"], color="g")
plt.plot(df["Ema_3"], color="r")
plt.plot(df["Ema_5"], color="r")
plt.plot(df["Ema_8"], color="r")
plt.plot(df["Ema_10"], color="r")
plt.plot(df["Ema_12"], color="r")
plt.plot(df["Ema_15"], color="r")
plt.plot(df["Ema_30"], color="b")
plt.plot(df["Ema_35"], color="b")
plt.plot(df["Ema_40"], color="b")
plt.plot(df["Ema_45"], color="b")
plt.plot(df["Ema_50"], color="b")
plt.plot(df["Ema_60"], color="b")
plt.title(f"Red White Blue Strategy for {stock.upper()} - {total_return}%")
plt.ylabel("Price")
plt.xlabel("Date")
plt.show()