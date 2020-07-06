import pandas as pd
import pandas_ta as ta
from pandas_datareader import DataReader
import datetime
import matplotlib.pyplot as plt

# Load data
symbol = 'AAPL'

num_of_years = 1
start_date = datetime.datetime.now() - datetime.timedelta(days=int(365.25 * num_of_years))
end_date = datetime.date.today()

df = DataReader(symbol, 'yahoo' ,start_date, end_date)

df.columns = map(str.lower, df.columns)

df.ta.strategy(name='all')

# Sanity check. Make sure all the columns are there
print(df.columns)
print(df.tail())
plt.plot(df['bbands'])