import pandas as pd
from pandas_datareader import DataReader
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import numpy as np

# Pull data for ticker, adj is split & dividend adjusted
num_of_years = 8
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 

stock = 'SPY'

data = DataReader(stock, "yahoo", start_date, end_date)

def lumpsum(invest_date, principal=10000): 
    invest_price = data.loc[invest_date]['Adj Close']
    current_price = data['Adj Close'][-1]
    
    investment_return = (current_price / invest_price) -1
    
    return principal*(1+investment_return)

def dollar_cost_average(invest_date, periods=12, freq='30D', principal=10000): 
    
    # Get DCA dates
    dca_dates =  investment_dates_all = pd.date_range(invest_date, periods=periods, freq=freq)
    
    # Filter out ones past the last data day
    dca_dates = dca_dates[dca_dates < data.index[-1]]
    
    # Figure out how many dates we cut off
    cut_off_count = 12 - len(dca_dates)

    # Amount you have in cash and not the market
    value = cut_off_count*(principal/periods)
    
    for date in dca_dates:
        # Get an actual trading day
        trading_date = data.index[data.index.searchsorted(date)]

        # Calculate lumpsum value if invested on that date, add to value
        value += lumpsum(trading_date, principal= principal/periods)
    
    return value


# Plot ticker 
data_price = data['Adj Close']

fig, ax = plt.subplots()

# Style and size
fig.set_size_inches(15, 7)

# Plot Series
ax.plot(data.index, data_price, color='black')

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax.yaxis.set_major_formatter(tick) 
ax.set_title(f'Adjusted {stock} Price', size=18)
ax.set_ylabel('Price ($)', size=14)
ax.set_xlabel('Date', size=14)
plt.legend()
plt.show()


# Lump Sum 
lump_sum = [lumpsum(x) for x in data.index]

# Dollar Cost Average 
dca = [dollar_cost_average(i) for i in data.index]

# Plot Together
# size
fig, ax = plt.subplots()
fig.set_size_inches(15, 7)

# Plot Series
ax.plot(data.index, lump_sum, color='black')
ax.plot(data.index, dca, color='red')

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax.yaxis.set_major_formatter(tick) 

# Labels
ax.set_title('DCA vs. Lump Sum Investing', size=18)
ax.set_ylabel('Current Value ($)', size=14)
ax.set_xlabel('Date of Investing', size=14)

plt.legend(['Lump Sum Value', 'DCA Value'])
plt.show()


# Difference between strategies 
# Get difference with array operations
difference = np.array(lump_sum) - np.array(dca)

# Style and size
fig, ax = plt.subplots()
fig.set_size_inches(15, 7)

# Plot Series
ax.fill_between(data.index, y1=difference, y2=0, color='green', where=difference > 0, edgecolor='black')
ax.fill_between(data.index, y1=difference, y2=0, color='red', where=difference < 0, edgecolor='black')
ax.plot(data.index, difference, color='black', linewidth=.4)

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax.yaxis.set_major_formatter(tick) 

ax.set_title('Lump Sum - DCA', size=18)
ax.set_ylabel('Current Value Difference($)', size=14)
ax.set_xlabel('Date of Investment', size=14)
plt.legend(['Amount','Lump Sum > DCA', 'DCA > Lump Sum'])
plt.show()


# ### Plot ticker, LS & DCA, and Difference
# Create Plots
fig, (ax1, ax2, ax3) = plt.subplots(3)

# Style and size
fig.set_size_inches(15, 7)

###### ticker Plot
ax1.plot(data.index, data_price, color='black')

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax1.yaxis.set_major_formatter(tick) 
ax1.set_title(f'Adjusted {stock} Price', size=18)
ax1.set_ylabel('Price ($)', size=14)
ax1.set_xlabel('Date', size=14)


###### LS & DCA Plot
# Plot Series
ax2.plot(data.index, lump_sum, color='black')
ax2.plot(data.index, dca, color='red')

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax2.yaxis.set_major_formatter(tick) 

# Labels
ax2.set_title('DCA vs. Lump Sum Investing', size=18)
ax2.set_ylabel('Current Value ($)', size=14)
ax2.set_xlabel('Date of Investment', size=14)

ax2.legend(['Lump Sum', 'DCA'])

###### Difference Plot
# Plot Series
ax3.fill_between(data.index, y1=difference, y2=0, color='green', where=difference > 0, edgecolor='black')
ax3.fill_between(data.index, y1=difference, y2=0, color='red', where=difference < 0, edgecolor='black')
ax3.plot(data.index, difference, color='black', linewidth=.4)

# Set Y axis format 
tick = ticker.StrMethodFormatter('${x:,.0f}')
ax3.yaxis.set_major_formatter(tick) 

ax3.set_title('Lump Sum - DCA', size=18)
ax3.set_ylabel('Current Value Difference($)', size=14)
ax3.set_xlabel('Date of Investment', size=14)
ax3.legend(['Amount','Lump Sum > DCA', 'DCA > Lump Sum'])

fig.tight_layout()
plt.show()

print("Lump sum beats Dollar Cost Averaging {:.2f}% of the time".format((100*sum(difference>0)/len(difference))))