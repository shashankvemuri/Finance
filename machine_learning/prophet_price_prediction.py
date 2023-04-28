# Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import datetime as dt
from fbprophet import Prophet

# Set the ticker symbol and number of years to retrieve data for
ticker = 'AAPL'
num_of_years = 20

# Set the start and end dates for retrieving data
start = dt.datetime.now() - dt.timedelta(days=int(365.25 * num_of_years))
now = dt.datetime.now() 

# Retrieve stock data using pandas_datareader
data = DataReader(ticker, 'yahoo', start, now)

# Reset the index and keep only the 'Date' and 'Close' columns
data = data.reset_index()
data = data[["Date","Close"]]

# Rename the columns to match the Prophet library's required input format
data = data.rename(columns = {"Date":"ds","Close":"y"}) 

# Create and fit a Prophet model to the data
m = Prophet(daily_seasonality=True) 
m.fit(data) 

# Create a dataframe with future dates to predict stock prices for
future = m.make_future_dataframe(periods=30)

# Make predictions with the Prophet model
prediction = m.predict(future)

# Plot the predicted stock prices
m.plot(prediction)
plt.title(f"Predicted Stock Price of {ticker} using Prophet")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.show()