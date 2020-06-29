import trendln
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
from pandas_datareader import data as pdr

yf.pdr_override()

stock = 'AAPL'

num_of_years = 1
start_date = datetime.datetime.now() - datetime.timedelta(int(365.25 * num_of_years))
end_date = datetime.datetime.now()

delta = start_date - end_date
x_data = np.arange(delta)

hist = pdr.get_data_yahoo(stock, start_date, end_date)
print (hist)

fig = trendln.plot_support_resistance(hist[-1000:].Close)
plt.show()