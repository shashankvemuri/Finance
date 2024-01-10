import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from pandas_datareader import data as pdr
import datetime as dt

# Function to fetch stock data
def fetch_stock_data(symbol, start, end):
    return pdr.get_data_yahoo(symbol, start, end)

# Lump Sum Investment Function
def lump_sum_investment(df, invest_date, principal):
    invest_price = df.loc[invest_date]['Adj Close']
    current_price = df['Adj Close'][-1]
    return principal * ((current_price / invest_price) - 1)

# Dollar-Cost Averaging Function
def dca_investment(df, invest_date, periods, freq, principal):
    dca_dates = pd.date_range(invest_date, periods=periods, freq=freq)
    dca_dates = dca_dates[dca_dates < df.index[-1]]
    cut_off_count = 12 - len(dca_dates)
    cut_off_value = cut_off_count * (principal / periods)
    dca_value = cut_off_value
    for date in dca_dates:
        trading_date = df.index[df.index.searchsorted(date)]
        dca_value += lump_sum_investment(df, trading_date, principal / periods)
    return dca_value

# User Input
symbol = input('Enter a ticker: ')
years = 20

# Set dates for data retrieval
start_date = dt.datetime.now() - dt.timedelta(days=int(365.25 * years))
end_date = dt.datetime.now()

# Fetch Data
stock_data = fetch_stock_data(symbol, start_date, end_date)

# Analysis for Lump Sum and DCA
lump_sum_values = [lump_sum_investment(stock_data, date) for date in stock_data.index]
dca_values = [dca_investment(stock_data, date, 12, '30D') for date in stock_data.index]

# Plotting
fig, axs = plt.subplots(3, 1, figsize=(15, 15))
axs[0].plot(stock_data.index, stock_data['Adj Close'], label=f'{symbol} Price')
axs[1].plot(stock_data.index, lump_sum_values, label='Lump Sum Investment')
axs[1].plot(stock_data.index, dca_values, label='DCA Investment')
axs[2].plot(stock_data.index, np.array(lump_sum_values) - np.array(dca_values), label='Difference in Investment Values')

# Setting labels, titles, and formats
for ax in axs:
    ax.legend()
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
axs[0].set_title(f'{symbol} Stock Price')
axs[1].set_title('Lump Sum vs. DCA Investment Value')
axs[2].set_title('Difference Between Lump Sum and DCA')

# Display the plots
plt.tight_layout()
plt.show()