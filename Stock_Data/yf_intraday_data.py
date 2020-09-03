import yfinance as yf
import matplotlib.pyplot as plt

stock = "NKE"
data = yf.download(tickers= stock, period="1d", interval="1m")
print (data.tail())
df = data['Close']
fig, ax = plt.subplots()
plt.plot(df)
plt.title('Price for {}'.format(stock))
plt.xlabel('Time')
plt.ylabel('Price')
plt.show()

'''
# Import TimeSeries class
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd

ALPHA_VANTAGE_API_KEY = ''

# Initialize the TimeSeries class with key and output format
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

# Get pandas dataframe with the intraday data and information of the data
intraday_data, data_info = ts.get_intraday(
 'ASMB', outputsize='full', interval='1min')

# Print the information of the data
print (data_info)

# Print the intraday data
print(intraday_data.head())

intraday_data['4. close'].plot(figsize=(10, 7))

# Define the label for the title of the figure
plt.title("Close Price", fontsize=16)

# Define the labels for x-axis and y-axis
plt.ylabel('Price', fontsize=14)
plt.xlabel('Time', fontsize=14)

# Plot the grid lines
plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
plt.show()

ohlcv_dict = {
 '1. open': 'first',
 '2. high': 'max',
 '3. low': 'min',
 '4. close': 'last',
 '5. volume': 'sum'
}

intraday_data.index = pd.to_datetime(intraday_data.index)
intraday_data_10 = intraday_data.resample('10T').agg(ohlcv_dict)
print (intraday_data_10.head())
'''
