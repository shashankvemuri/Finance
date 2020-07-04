import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import warnings
warnings.filterwarnings("ignore") 
import yfinance as yf
yf.pdr_override()
import datetime as dt

symbol = 'AAPL'

num_of_years = 5
start = dt.date.today() - dt.timedelta(days=365*num_of_years)
end = dt.date.today()

dataset = yf.download(symbol,start,end)

class stock_data:
    def __init__(self):
        pass
    
    def function(self):
        print("Here my stock data:\n", dataset)

myobject = stock_data
print(myobject.function(dataset))

class ExploratoryData:
    # Initialize class with self argument
    def __init__(self):
        pass
    
    # Define class method which takes self argument: print_stock_summary
    def print_stock_summary(self):
        # Print string
        print("__________________Exploratory Data Analysis__________________")
        print("Stock Data")
        print('-'*60)
        print("Dataset information") 
        print(dataset.info(memory_usage='deep',verbose=False))
        print('-'*60)
        print(dataset.info())
        print('-'*60)
        print("Data type:")
        print(dataset.dtypes)
        print('-'*60)
        print("Check unique values wihtout NaN")
        print(dataset.nunique())
        print('-'*60)
        print("Data shape:")
        print(dataset.shape)
        print('-'*60)
        print("Data columns Names:")
        print(dataset.columns)
        print('-'*60)
        print("Check for NaNs:")
        print(dataset.isnull().values.any())
        print("Check for NaNs in rows:")
        print(dataset.isnull().sum(axis = 0))
        print("Check for NaNs in columns:")
        print(dataset.isnull().sum(axis = 1))
        print('-'*60)
        print("Data Statistics Summary:")
        print(dataset.describe())


ExploratoryData.print_stock_summary(dataset)

class StockReturns:
  
	# Initialize class with self and stockData as arguments
    def __init__(self, stockData):
      	# Set data as instance variable, and assign it the value of stockData
        self.data = stockData
    
    # Define Log Returns
    def stock_log(self):
        log_returns = np.log(dataset['Adj Close'].shift(-1)) - np.log(dataset['Adj Close'])
        return log_returns
    
	# Define MU
    def stock_mu(self):
        log_returns = np.log(dataset['Adj Close'].shift(-1)) - np.log(dataset['Adj Close'])
        mu = log_returns.mean()
        return mu
        
    # Define Sigma
    def stock_sigma(self):
        log_returns = np.log(dataset['Adj Close'].shift(-1)) - np.log(dataset['Adj Close'])
        sigma = log_returns.std(ddof=1)
        return sigma


stock_data = StockReturns(dataset)

print(stock_data.stock_log())
print(stock_data.stock_log().head())
print(stock_data.stock_mu())
print(stock_data.stock_sigma())

class Stock_Data:
    # Stock_Family = 'DataStock'
    def __init__(self): 
        self.data = dataset


class Plot_Line(Stock_Data):
    def __init__(self):
        f = plt.figure(figsize=(14,10))
        plt.plot(self.data['Adj Close'])
        plt.legend(loc='best')
        plt.title('Stock Closing Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        return f
    
# Define class Plot_hist
class Plot_hist(Stock_Data):
    def __init__(self):
        f = plt.figure(figsize=(14,10))
        plt.hist(self.data['Adj Close'])
        plt.legend(loc='best')
        plt.title('Stock Closing Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        return f


class Stock_Data(object):
    def __init__(self): 
        pass
      
    # Define class Plot_Line
    def Plot_Line(self):
        plt.figure(figsize=(14,10))
        plt.plot(dataset['Adj Close'])
        plt.legend(loc='best')
        plt.title('Stock Closing Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        return 
    
    # Define class Plot_hist
    def Plot_hist(sef):
        f = plt.figure(figsize=(14,10))
        plt.hist(dataset['Adj Close'])
        plt.title('Stock Closing Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        return

Stock_Data.Plot_Line(dataset)
Stock_Data.Plot_hist(dataset)

class Stock:
	# Initialize class with self, symbol, start, and end as arguments
    def __init__(self, symbol, start, end):
      	# Set data as instance variable, and assign it the variables of stock
        self.symbol = symbol
        self.start = start
        self.end = end
    
    def get_descriptive_data(self):
        dataset = yf.download(self.symbol,self.start,self.end)
        return dataset


df = Stock(symbol, start, end)
print(df.get_descriptive_data())