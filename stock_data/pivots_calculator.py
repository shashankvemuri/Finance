import datetime as dt
import matplotlib.pyplot as plt
import yfinance

# Set display options for Pandas
import pandas as pd
pd.set_option('display.max_columns', None)

# Prompt user for stock ticker input
stock = input('Enter a ticker: ')

# Fetch historical data for the specified stock using yfinance
ticker = yfinance.Ticker(stock)
df = ticker.history(interval="1d")

# Extract data for the last trading day and remove unnecessary columns
last_day = df.tail(1).copy().drop(columns=['Dividends', 'Stock Splits'])

# Calculate pivot points and support/resistance levels
# Pivot point formula: (High + Low + Close) / 3
last_day['Pivot'] = (last_day['High'] + last_day['Low'] + last_day['Close']) / 3
last_day['R1'] = 2 * last_day['Pivot'] - last_day['Low']  # Resistance 1
last_day['S1'] = 2 * last_day['Pivot'] - last_day['High']  # Support 1
last_day['R2'] = last_day['Pivot'] + (last_day['High'] - last_day['Low'])  # Resistance 2
last_day['S2'] = last_day['Pivot'] - (last_day['High'] - last_day['Low'])  # Support 2
last_day['R3'] = last_day['Pivot'] + 2 * (last_day['High'] - last_day['Low'])  # Resistance 3
last_day['S3'] = last_day['Pivot'] - 2 * (last_day['High'] - last_day['Low'])  # Support 3

# Display calculated pivot points and support/resistance levels for the last trading day
print(last_day)

# Fetch intraday data for the specified stock
data = yfinance.download(tickers=stock, period="1d", interval="1m")

# Extract 'Close' prices from the intraday data for plotting
df = data['Close']

# Create and configure the plot with support and resistance lines
fig, ax = plt.subplots()
plt.rcParams['figure.figsize'] = (15, 10)
plt.plot(df)
plt.axhline(last_day['R1'].tolist()[0], color='b', label='Resistance 1')
plt.axhline(last_day['S1'].tolist()[0], color='b', label='Support 1')
plt.axhline(last_day['R2'].tolist()[0], color='green', label='Resistance 2')
plt.axhline(last_day['S2'].tolist()[0], color='green', label='Support 2')
plt.axhline(last_day['R3'].tolist()[0], color='r', label='Resistance 3')
plt.axhline(last_day['S3'].tolist()[0], color='r', label='Support 3')
plt.legend()
plt.title(f'{stock.upper()} - {dt.date.today()}')
plt.xlabel('Time')
plt.ylabel('Price')

# Display the final plot
plt.show()