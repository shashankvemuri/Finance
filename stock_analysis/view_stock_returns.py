# Import dependencies
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib import dates as mdates
import datetime as dt

# Use yfinance to fetch stock data for the last five years
symbol = 'AAPL'
start_date = dt.date.today() - dt.timedelta(days=365*5)
end_date = dt.date.today()
dataset = yf.download(symbol, start_date, end_date)

# Plot the adjusted closing price over time
plt.figure(figsize=(15, 10))
plt.plot(dataset['Adj Close'])
plt.title('Closing Price Chart')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(True)
plt.subplots()
plt.show()

# Calculate monthly returns
monthly_dataset = dataset.asfreq('BM')
monthly_dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
monthly_dataset['Month_Name'] = monthly_dataset.index.strftime('%b')
monthly_dataset['Month_Name_Year'] = monthly_dataset.index.strftime('%b-%Y')
monthly_dataset = monthly_dataset.reset_index()
monthly_dataset['Month'] = monthly_dataset['Date'].dt.month

# Plot monthly returns as bar chart
plt.figure(figsize=(15, 10))
monthly_dataset['Returns'].plot(kind='bar')
plt.xlabel('Months')
plt.ylabel('Returns')
plt.title('Returns for Each Month')
plt.show()

# Plot monthly returns as bar chart with month labels
plt.figure(figsize=(15, 10))
monthly_dataset['Returns'].plot(kind='bar')
plt.xlabel('Months')
plt.ylabel('Returns')
plt.title('Returns for Each Month')
plt.xticks(monthly_dataset.index, monthly_dataset['Month_Name'])
plt.show()

# Plot monthly returns as bar chart with positive returns in green and negative returns in red
monthly_dataset['ReturnsPositive'] = monthly_dataset['Returns'] > 0
monthly_dataset['Date'] = pd.to_datetime(monthly_dataset['Date'])
monthly_dataset['Date'] = monthly_dataset['Date'].apply(mdates.date2num)
colors = monthly_dataset['ReturnsPositive'].map({True: 'g', False: 'r'})
plt.figure(figsize=(15, 10))
monthly_dataset['Returns'].plot(kind='bar', color=colors)
plt.xlabel('Months')
plt.ylabel('Returns')
plt.title('Returns for Each Month ' + str(start_date) + ' to ' + str(end_date))
plt.xticks(monthly_dataset.index, monthly_dataset['Month_Name'])
plt.show()

# Calculate yearly returns
yearly_dataset = dataset.asfreq('BY')
yearly_dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
yearly_dataset = yearly_dataset.reset_index()
yearly_dataset['Years'] = yearly_dataset['Date'].dt.year

# Plot yearly returns as bar chart with positive returns in green and negative returns in red
yearly_dataset['ReturnsPositive'] = yearly_dataset['Returns'] > 0
yearly_dataset['Date'] = pd.to_datetime(yearly_dataset['Date'])
yearly_dataset['Date'] = yearly_dataset['Date'].apply(mdates.date2num)
colors = yearly_dataset['ReturnsPositive'].map({True: 'g', False: 'r'})
plt.figure(figsize=(15, 10))
plt.bar(yearly_dataset['Years'], yearly_dataset['Returns'], color=colors, align='center')
plt.title('Yearly Returns')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.show()

# Calculate yearly returns average
dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
yearly_returns_avg = dataset['Returns'].groupby([dataset.index.year]).mean()
print(yearly_returns_avg)