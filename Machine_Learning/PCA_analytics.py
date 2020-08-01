# Get Dependencis
import numpy as np 
from pandas_datareader import data as pdr
import pandas as pd
import matplotlib.pyplot as plt
from yahoo_fin import stock_info as si
import datetime
import yfinance as yf
from sklearn.decomposition import PCA
from pylab import rcParams

yf.pdr_override()

# Set parameters
num_of_years = 1
start_date = datetime.date.today() - datetime.timedelta(days= (int(365.25*num_of_years)))
end_date = datetime.date.today()

# Get Data (if needed)
tickers = si.tickers_sp500()
tickers = [item.replace('.', '-') for item in tickers]
# prices = pdr.get_data_yahoo(tickers, start_date, end_date)['Adj Close']
# prices.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/S&P500_stock_prices.csv')

# Get Market Data
index = '^GSPC'
market_prices = pdr.get_data_yahoo(index, start_date, end_date)['Adj Close']
market_rs = market_prices.apply(np.log).diff(1) 

# Read in stock data and collect returns
prices = pd.read_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/S&P500_stock_prices.csv', index_col=0, parse_dates=True)
rs = prices.apply(np.log).diff(1) 
rcParams['figure.figsize'] = 15, 10
plt.plot(rs)
plt.title('Daily Returns of the Stocks in the S&P500')
plt.show()

# Calculate Cumulative Returns
crs = rs.cumsum().apply(np.exp)
rcParams['figure.figsize'] = 15, 10
plt.subplots()
plt.plot(crs)
plt.title('Cumulative Returns of the Stocks in the S&P500')
plt.show()

# PCA-Reduced Data
pca = PCA(1).fit(rs.fillna(0))
pc1 = pd.Series(index=rs.columns, data=pca.components_[0])
rcParams['figure.figsize'] = 15, 10
plt.subplots()
plt.plot(pc1)
plt.title('First Principal Component of the S&P500')
plt.show()

# Find PCA Portfolio equivalent of S&P 500
weights = abs(pc1)/sum(abs(pc1)) # l1norm = 1
myrs = (weights*rs).sum(1)
rs_df = pd.concat([myrs, market_rs], 1)
rs_df.columns = ["PCA Portfolio", "S&P500"]
crs_df = rs_df.cumsum().apply(np.exp)
rcParams['figure.figsize'] = 15, 10
plt.subplots()
plt.plot(crs_df)
plt.title('PCA Portfolio vs. S&P 500')
plt.show()

# Plot stocks with the most and least negative PCA Weights
fig, ax = plt.subplots(2,1)
rcParams['figure.figsize'] = 15, 10
pc1.nsmallest(10).plot.bar(ax=ax[0], color='red', grid=True, title='Stocks with Most and Least Negative PCA Weights')
pc1.nlargest(10).plot.bar(ax=ax[1], color='green', grid=True)

# Plot best PCA Porfolio vs. S&P 500
myrs = rs[pc1.nlargest(10).index].mean(1)
mycrs = myrs.cumsum().apply(np.exp)
market_crs = market_rs.cumsum().apply(np.exp)
rcParams['figure.figsize'] = 15, 10
plt.subplots()
plt.plot(mycrs)
plt.plot(market_crs)
plt.title('PCA Selection vs. S&P500')
plt.legend(['PCA Selection', 'S&P500'])