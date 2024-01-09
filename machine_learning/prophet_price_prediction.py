# Import necessary libraries
import pandas as pd
import datetime as dt
from pandas_datareader import DataReader
from fbprophet import Prophet
import matplotlib.pyplot as plt

# Set ticker symbol and data retrieval duration
ticker = 'AAPL'
num_years = 20
start_date = dt.datetime.now() - dt.timedelta(days=365.25 * num_years)
end_date = dt.datetime.now()

# Fetch stock data
data = DataReader(ticker, 'yahoo', start_date, end_date)

# Prepare data for Prophet model
data.reset_index(inplace=True)
data = data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

# Initialize and fit Prophet model
model = Prophet(daily_seasonality=True)
model.fit(data)

# Prepare future dataframe for prediction
future = model.make_future_dataframe(periods=30)

# Make predictions
forecast = model.predict(future)

# Plot predictions
model.plot(forecast)
plt.title(f"Predicted Stock Price of {ticker} using Prophet")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.show()