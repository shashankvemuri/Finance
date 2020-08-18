import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
from matplotlib import dates as mdates
import datetime as dt

# input
symbol = 'AAPL'
start = dt.date.today() - dt.timedelta(days = 365*5)
end = dt.date.today()

# Read data 
dataset = yf.download(symbol,start,end)

plt.figure(figsize=(15,10))
plt.plot(dataset['Adj Close'])
plt.title('Closing Price Chart')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(True)
plt.subplots()
plt.show()

monthly = dataset.asfreq('BM')
monthly['Returns'] = dataset['Adj Close'].pct_change().dropna()

monthly['Month_Name'] = monthly.index.strftime("%b")
monthly['Month_Name_Year'] = monthly.index.strftime("%b-%Y")

monthly = monthly.reset_index()
monthly['Month'] = monthly["Date"].dt.month

monthly['Returns'].plot(kind='bar', figsize=(15,10))
plt.xlabel("Months")
plt.ylabel("Returns")
plt.title("Returns for Each Month")
plt.show()

monthly['Returns'].plot(kind='bar', figsize=(15,10))
plt.xlabel("Months")
plt.ylabel("Returns")
plt.title("Returns for Each Month")
plt.xticks(monthly.index, monthly['Month_Name'])
plt.show()

monthly['ReturnsPositive'] = 0 < monthly['Returns']
monthly['Date'] = pd.to_datetime(monthly['Date'])
monthly['Date'] = monthly['Date'].apply(mdates.date2num)

colors = monthly.ReturnsPositive.map({True: 'g', False: 'r'})
monthly['Returns'].plot(kind='bar', color = colors, figsize=(15,10))
plt.xlabel("Months")
plt.ylabel("Returns")
plt.title("Returns for Each Month " + str(start) + ' to ' + str(end))
plt.xticks(monthly.index, monthly['Month_Name'])
plt.show()

yearly = dataset.asfreq('BY')
yearly['Returns'] = dataset['Adj Close'].pct_change().dropna()
yearly = yearly.reset_index()
yearly['Years'] = yearly['Date'].dt.year
print(yearly)

yearly['ReturnsPositive'] = 0 < yearly['Returns']
yearly['Date'] = pd.to_datetime(yearly['Date'])
yearly['Date'] = yearly['Date'].apply(mdates.date2num)

colors = yearly.ReturnsPositive.map({True: 'g', False: 'r'})
plt.gcf()
plt.gcf()
plt.figure(figsize=(15,10))
plt.bar(yearly['Years'], yearly['Returns'], color=colors, align='center')
plt.title('Yearly Returns')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.show()

dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
yearly_returns_avg = dataset['Returns'].groupby([dataset.index.year]).mean()
print(yearly_returns_avg)