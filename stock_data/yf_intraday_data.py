# Import dependencies
import yfinance as yf
import matplotlib.pyplot as plt

# Define the stock symbol
symbol = "NKE"

# Download the intraday data for the stock
data = yf.download(tickers=symbol, period="1d", interval="1m")

# Print the last 5 rows of the data
print(data.tail())

# Extract the close prices from the data
close_prices = data['Close']

# Create a plot of the close prices
fig, ax = plt.subplots()
ax.plot(close_prices)
ax.set_title('Price for {}'.format(symbol))
ax.set_xlabel('Time')
ax.set_ylabel('Price')
plt.show()