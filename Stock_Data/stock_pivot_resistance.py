# Import dependencies
import yfinance as yf
import datetime as dt
import pandas_datareader as pdr
import matplotlib.pyplot as plt

# Override pandas_datareader's default behavior to use yfinance instead of Yahoo Finance API
yf.pdr_override()

# Set the date range for which to fetch the stock data
start_date = dt.datetime(2019, 6, 1)
end_date = dt.datetime.now()

# Get the stock symbol from the user
stock_symbol = input("Enter the stock symbol: ")

# Keep asking for the stock symbol until the user enters "quit"
while stock_symbol.lower() != "quit":

    # Fetch the stock data from Yahoo Finance
    df = pdr.get_data_yahoo(stock_symbol, start_date, end_date)

    # Plot the high prices of the stock over time
    df["High"].plot(label="High")

    # Find the pivot points (local maxima) in the stock's high prices
    pivots = []
    dates = []
    counter = 0
    last_pivot = 0

    # Create a sliding window of size 10 to find local maxima
    window_size = 10
    window = [0] * window_size
    date_window = [0] * window_size

    for i, high_price in enumerate(df["High"]):
        window = window[1:] + [high_price]
        date_window = date_window[1:] + [df.index[i]]

        current_max = max(window)
        if current_max == last_pivot:
            counter += 1
        else:
            counter = 0

        if counter == 5:
            last_pivot = current_max
            last_date = date_window[window.index(last_pivot)]

            pivots.append(last_pivot)
            dates.append(last_date)

    # Print the pivot points and their dates
    for i in range(len(pivots)):
        print(f"{pivots[i]}: {dates[i].date()}")

        # Plot the resistance levels for each pivot point
        time_delta = dt.timedelta(days=30)
        plt.plot_date([dates[i], dates[i]+time_delta],
                      [pivots[i], pivots[i]],
                      linestyle="-", linewidth=2, marker=",")

    # Set the plot's title and display it
    plt.title(stock_symbol.upper() + ' Resistance Points')
    plt.gcf().autofmt_xdate()
    plt.subplots_adjust(bottom=0.2)
    plt.show()

    # Ask the user for another stock symbol
    stock_symbol = input("Enter another stock symbol (or type 'quit' to exit): ")