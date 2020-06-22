import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
from pandas_datareader import DataReader
import time 

yf.pdr_override() 

num_of_years = 40
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.datetime.now() 

#Asks for stock ticker
stocks = pd.read_csv('russell3000_tickers.csv')['Ticker']

watch = []
watch_pct = []
watch_mean = []
watch_std = []

def_watch = [] 
def_watch_pct = []
def_watch_mean = []
def_watch_std = []

must_watch = []
must_watch_pct = []
must_watch_mean = []
must_watch_std = []

for stock in stocks: 
    try:
        time.sleep(1)
        df = DataReader(stock, 'yahoo' ,start, now)
        df = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    
        sma = 50
        limit = 10
        
        #calculates sma and creates a column in the dataframe
        df['SMA'+str(sma)] = df.iloc[:,4].rolling(window=sma).mean() 
        df['PC'] = ((df["Adj Close"]/df['SMA'+str(sma)])-1)*100
        
        mean = round(df["PC"].mean(), 3)
        stdev = round(df["PC"].std(), 3)
        current = round(df["PC"][-1], 3)
        yday = round(df["PC"][-2], 3)
        
        print (stock)
        print(f'Current % away from {sma}-day SMA: ' + str(current))
        print("Mean: " + str(mean))
        print("Standard Dev: " + str(stdev))
        print ('-'*52)
    
        if abs(float(current)) > abs(float(1*stdev+mean)):
            watch.append(stock)
            watch_pct.append(current)
            watch_mean.append(mean)
            watch_std.append(stdev)
            
        elif abs(float(current)) > abs(float(2*stdev+mean)):
            def_watch.append(stock)
            def_watch_pct.append(current)
            def_watch_mean.append(mean)
            def_watch_std.append(stdev)
        
        elif abs(float(current)) > abs(float(3*stdev+mean)):
            must_watch.append(stock)
            must_watch_pct.append(current)
            must_watch_mean.append(mean)
            must_watch_std.append(stdev)
    except:
        pass
    
print ('Watch:')
df1 = pd.DataFrame(list(zip(watch, watch_pct, watch_mean, watch_std)), columns =['Company', 'Current', 'Mean', 'Standard Deviation'])
df1 = df1.set_index('Company')
df1.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/watch.csv')
print (df1)

print ('\n')
print ('Def Watch:')
df2 = pd.DataFrame(list(zip(def_watch, def_watch_pct, def_watch_mean, def_watch_std)), columns =['Company', 'Current', 'Mean', 'Standard Deviation'])
df2 = df2.set_index('Company')
df2.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/def_watch.csv')
print (df2)

print ('\n')
print ('Must Watch:')
df3 = pd.DataFrame(list(zip(must_watch, must_watch_pct, must_watch_mean, must_watch_std)), columns =['Company', 'Current', 'Mean', 'Standard Deviation'])
df3 = df3.set_index('Company')
df3.to_csv('/Users/shashank/Documents/Code/Python/Outputs/csv/must_watch.csv')
print (df3)
