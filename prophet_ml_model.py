import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import datetime as dt
from fbprophet import Prophet

ticker = 'AAPL'
num_of_years = 20
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.datetime.now() 

data = DataReader(ticker, 'yahoo', start, now)
data = data.reset_index()

data = data[["Date","Close"]]
data = data.rename(columns = {"Date":"ds","Close":"y"}) 

m = Prophet(daily_seasonality = True) 
m.fit(data) 

future = m.make_future_dataframe(periods=30) 
prediction = m.predict(future)
m.plot(prediction)
plt.title(f"Prediction of the {ticker}'s Stock Price using the Prophet")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.show()