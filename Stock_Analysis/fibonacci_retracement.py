# Import dependencies
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import pandas as pd 
import datetime 

# Define the stock ticker and the start and end dates for data retrieval
stock_ticker = 'AAPL'
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.date.today()

# Retrieve the stock data using the Yahoo Finance API
stock_data = DataReader(stock_ticker, 'yahoo', start_date, end_date)

# Plot the price series
fig, ax = plt.subplots()
ax.plot(stock_data['Close'], color='black')

# Define the minimum and maximum price points for the stock
price_min = stock_data['Close'].min()
price_max = stock_data['Close'].max()

# Calculate the Fibonacci retracement levels
diff = price_max - price_min
fib_level_1 = price_max - 0.236 * diff
fib_level_2 = price_max - 0.382 * diff
fib_level_3 = price_max - 0.618 * diff

fib_levels = [0, 0.236, 0.382, 0.618, 1]
fib_prices = [price_max, fib_level_1, fib_level_2, fib_level_3, price_min]

# Create a Pandas DataFrame to store the Fibonacci retracement levels and prices
fibonacci_df = pd.DataFrame(list(zip(fib_levels, fib_prices)), columns=['Levels', 'Prices']) 

print(fibonacci_df)

# Shade the regions between the Fibonacci levels
ax.axhspan(fib_level_1, price_min, alpha=0.4, color='lightsalmon')
ax.axhspan(fib_level_2, fib_level_1, alpha=0.5, color='palegoldenrod')
ax.axhspan(fib_level_3, fib_level_2, alpha=0.5, color='palegreen')
ax.axhspan(price_max, fib_level_3, alpha=0.5, color='powderblue')
plt.ylabel("Price")
plt.xlabel("Date")
plt.legend(loc=2)
plt.show()