import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt

# Set up the input variables
symbols = ['AAPL', 'MSFT', 'AMD', 'INTC', 'NVDA']
start = dt.date.today() - dt.timedelta(days=365*3)
end = dt.date.today()

# Create an empty DataFrame
df = pd.DataFrame()
data = []

# Loop through each stock ticker, download the stock data, and add it to the DataFrame
for symbol in symbols:
    # Download the stock data
    stock_data = yf.download(symbol, fields='price', start=start, end=end)

    # Extract the adjusted closing prices and merge with the main DataFrame
    adj_close = pd.DataFrame(stock_data['Adj Close'])
    df = pd.merge(df, adj_close, right_index=True, left_index=True, how='outer')

    # Append the stock ticker to the list of tickers with available data
    data.append(symbol)

# Set the column names of the DataFrame to the tickers with available data
df.columns = data

# Drop any columns that have missing data
df = df.dropna(axis='columns')

# Calculate the percentage change in stock prices over the past 3 periods
rets = df.pct_change(periods=3)

# Create a scatter plot matrix of the percentage changes in stock prices
from pandas.plotting import scatter_matrix
scatter_matrix(rets, diagonal='kde', figsize=(10, 10))

# Calculate the correlation matrix of the percentage changes in stock prices
corr = rets.corr()

# Create a heatmap of the correlation matrix
plt.imshow(corr, cmap='Blues', interpolation='none')
plt.colorbar()
plt.xticks(range(len(corr)), corr.columns)
plt.yticks(range(len(corr)), corr.columns)

# Create a bar chart of the standard deviations of the percentage changes in stock prices
plt.bar(rets.columns, rets.std(), color=['red', 'blue', 'green', 'orange', 'cyan'])
plt.title("Stock Risk")
plt.xlabel("Stock Symbols")
plt.ylabel("Standard Deviations")

# Create a bar chart of the average percentage changes in stock prices
plt.bar(rets.columns, rets.mean(), color=['red', 'blue', 'green', 'orange', 'cyan'])
plt.title("Average Returns")
plt.xlabel("Stock Symbols")
plt.ylabel("Returns")

# Create a bar chart comparing the average percentage changes in stock prices to their standard deviations
ind = np.arange(5)
width = 0.35       
plt.bar(ind, rets.mean(), width, color='g', label='Average of Returns')
plt.bar(ind + width, rets.std(), width, color='r', label='Risk of Returns')
plt.ylabel('Returns Scores')
plt.xlabel('Symbols')
plt.title('Risk vs Return')
plt.xticks(ind + width / 2, ('AAPL', 'MSFT', 'AMD', 'INTC', 'NVDA'))
plt.legend(loc='best')

# Create stacked bar charts comparing the average percentage changes in stock prices to their standard deviations
ind = [x for x, _ in enumerate(symbols)]
plt.bar(ind, rets.mean(), width=0.8, label='Average of Returns', color='b')
plt.bar(ind, rets.std(), width=0.8, label='Risk of Returns', color='r', bottom=rets.mean())
plt.xticks(ind, symbols)
plt.ylabel("Returns Score")
plt.xlabel("Symbols")
plt.legend(loc="upper right")
plt.title('Risk vs Return')
plt.subplots()
plt.show()

# Create scatter plot to show expected returns vs risk
plt.scatter(rets.mean(), rets.std())
plt.xlabel('Expected returns')
plt.ylabel('Risk')
for label, x, y in zip(rets.columns, rets.mean(), rets.std()):
    plt.title('Risk vs Expected Returns')
    plt.annotate(
        label, 
        xy = (x, y), xytext = (20, -20),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.7', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
plt.subplots()
plt.show()

# Display table with risk vs expected returns
d = {'Risk':rets.std(), 'Expected Returns':rets.mean()}
print('Table: Risk vs Expected Returns')
tables = pd.DataFrame(data=d)
print (tables)