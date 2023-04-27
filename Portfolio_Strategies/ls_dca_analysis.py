# Import dependencies
import pandas as pd
from pandas_datareader import DataReader
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import numpy as np

# Set default figure size
plt.rcParams['figure.figsize'] = (15, 10)

# Define number of years for data retrieval
num_of_years = 20
# Calculate start and end dates for data retrieval
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 

# Prompt user for stock ticker
stock = input('Enter a ticker: ')

# Retrieve stock data from Yahoo Finance API
data = DataReader(stock, "yahoo", start_date, end_date)

def lumpsum(invest_date, principal=10000):
    """Calculate investment return for lump sum investing."""
    invest_price = data.loc[invest_date]['Adj Close']
    current_price = data['Adj Close'][-1]
    
    investment_return = (current_price / invest_price) -1
    
    return principal*(1+investment_return)

def dollar_cost_average(invest_date, periods=12, freq='30D', principal=10000): 
    """Calculate investment return for dollar-cost averaging."""
    dca_dates = pd.date_range(invest_date, periods=periods, freq=freq)
    # Drop dates that are beyond the data's last date
    dca_dates = dca_dates[dca_dates < data.index[-1]]
    
    # Calculate the amount of money that can't be invested due to the cut-off of the last date
    cut_off_count = 12 - len(dca_dates)
    cut_off_value = cut_off_count*(principal/periods)
    
    # Calculate the value of the invested money
    dca_value = cut_off_value
    for date in dca_dates:
        trading_date = data.index[data.index.searchsorted(date)]
        dca_value += lumpsum(trading_date, principal= principal/periods)
    return dca_value

# Plot ticker 
data_price = data['Adj Close']
fig, ax = plt.subplots()

# Plot ticker data
ax.plot(data.index, data_price, color='black')

# Format Y-axis
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax.yaxis.set_major_formatter(tick) 
ax.set_title(f'Adjusted {stock} Price', size=18)
ax.set_ylabel('Price ($)', size=14)
ax.set_xlabel('Date', size=14)
plt.show()

# Calculate investment returns for lump sum and dollar-cost averaging
lump_sum = [lumpsum(x) for x in data.index]
dca = [dollar_cost_average(i) for i in data.index]

# Plot investment returns for both strategies
fig, ax = plt.subplots()
ax.plot(data.index, lump_sum, color='black')
ax.plot(data.index, dca, color='red')

# Format Y-axis
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax.yaxis.set_major_formatter(tick) 

# Add labels and title
ax.set_title('DCA vs. Lump Sum Investing', size=18)
ax.set_ylabel('Current Value ($)', size=14)
ax.set_xlabel('Date of Investing', size=14)
plt.legend(['Lump Sum Value', 'DCA Value'])
plt.show()

# Calculate the difference in investment returns between the two strategies
difference = np.array(lump_sum) - np.array

# Style
fig, ax = plt.subplots()

# Plot Series
ax.fill_between(data.index, y1=difference, y2=0, color='green', where=difference > 0, edgecolor='black')
ax.fill_between(data.index, y1=difference, y2=0, color='red', where=difference < 0, edgecolor='black')
ax.plot(data.index, difference, color='black', linewidth=.4)

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax.yaxis.set_major_formatter(tick) 

ax.set_title('Lump Sum - DCA', size=18)
ax.set_ylabel('Current Value Difference($)', size=14)
plt.legend(['Amount','Lump Sum > DCA', 'DCA > Lump Sum'])
plt.show()

# Plot Price History, LS & DCA, and LS & DCA Performance Difference
fig, (ax1, ax2, ax3) = plt.subplots(3)

# Price History
ax1.plot(data.index, data_price, color='black')

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax1.yaxis.set_major_formatter(tick) 
ax1.set_title(f'Adjusted {stock} Price', size=18)
ax1.set_ylabel('Price ($)', size=14)
ax1.set_xlabel('Date', size=14)

# Plot LS & DCA
ax2.plot(data.index, lump_sum, color='black')
ax2.plot(data.index, dca, color='red')

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax2.yaxis.set_major_formatter(tick) 

# Labels
ax2.set_title('DCA vs. Lump Sum Investing', size=18)
ax2.set_ylabel('Current Value ($)', size=14)
ax2.legend(['Lump Sum', 'DCA'])

# Plot LS & DCA Performance Difference
ax3.fill_between(data.index, y1=difference, y2=0, color='green', where=difference > 0, edgecolor='black')
ax3.fill_between(data.index, y1=difference, y2=0, color='red', where=difference < 0, edgecolor='black')
ax3.plot(data.index, difference, color='black', linewidth=.4)

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax3.yaxis.set_major_formatter(tick) 

# Labels
ax3.set_title('Lump Sum - DCA', size=18)
ax3.set_ylabel('Current Value Difference($)', size=14)
ax3.legend(['Amount','Lump Sum > DCA', 'DCA > Lump Sum'])

# Show Plot
fig.tight_layout()
plt.show()

# Print out the difference
print("Lump Sum Investing Beats Dollar Cost Averaging {:.2f}% of the time".format((100*sum(difference>0)/len(difference))))