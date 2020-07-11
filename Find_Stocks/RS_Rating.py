from pandas_datareader import DataReader
from yahoo_fin import stock_info as si
import pandas as pd
import requests
import datetime
import time


stocklist = si.tickers_sp500()
stocklist = [item.replace(".", "-") for item in stocklist]

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

index_name = '^GSPC' # S&P 500
n = -1

start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

# df = DataReader(stocklist, 'yahoo' ,start=start_date, end=end_date)['Adj Close']
# df.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/all_sp500.csv')

# index_df = DataReader(index_name, 'yahoo', start=start_date, end=end_date)
# index_df.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/index_df.csv')['Adj Close']

RS = []

'''
for stock in stocklist:
    n += 1
    print ("\npulling {} with index {}".format(stock, n))
    
    df = pd.read_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/all_sp500.csv')
    df = df[f'{stock}']
    df['Percent Change'] = df.pct_change()    
    stock_return = df['Percent Change'].sum() * 100
    
    index_df = pd.read_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/index_df.csv')
    index_df['Percent Change'] = index_df['Adj Close'].pct_change()
    index_return = index_df['Percent Change'].sum() * 100
    
    RS_Rating = round((stock_return / index_return) * 10, 2)
    
    print ('Relative Strength: ' + str(RS_Rating))
    RS.append(RS_Rating)

dataframe = pd.DataFrame(list(zip(stocklist, RS)), columns =['Company', 'Relative Strength'])
dataframe.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/RS_Rating/{today}.csv')
print (dataframe)
'''

data = pd.read_csv(f'/Users/shashank/Documents/Code/Python/Outputs/RS_Rating/{today}.csv', index_col=1)
data = data.drop(columns = ['Unnamed: 0'])
data = data.sort_values('Relative Strength', ascending=False)
print (data.head(50))
