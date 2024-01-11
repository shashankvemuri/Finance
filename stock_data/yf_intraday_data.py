# Importing necessary libraries
import yfinance as yf
import matplotlib.pyplot as plt

# Function to download intraday data for a given stock symbol
def download_intraday_data(stock_symbol):
    data = yf.download(tickers=stock_symbol, period="1d", interval="1m")
    return data

# Function to plot close prices of the stock
def plot_close_prices(stock_data, stock_symbol):
    close_prices = stock_data['Close']
    
    # Creating the plot
    fig, ax = plt.subplots()
    ax.plot(close_prices)
    ax.set_title(f'Price for {stock_symbol}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    plt.show()

# Main script execution
if __name__ == "__main__":
    symbol = "NKE"  # Define the stock symbol

    # Downloading the intraday data
    intraday_data = download_intraday_data(symbol)

    # Printing the last 5 rows of the data
    print(intraday_data.tail())

    # Plotting the close prices
    plot_close_prices(intraday_data, symbol)
