import yfinance as yf
import datetime as dt
import pandas as pd
import time
from yahoo_fin import stock_info as si

pd.set_option('display.max_columns', None)

mylist = []
today = dt.date.today()
mylist.append(today)
today = mylist[0]

#Asks for stock ticker
stocks = si.tickers_sp500()
stocks = [item.replace(".", "-") for item in stocks]

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
        df = pd.read_csv(f'/Users/shashank/Documents/Code/Python/Outputs/S&P500/{stock}.csv', index_col=0)
        df = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
        df.index = pd.to_datetime(df.index)
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
    
        if abs(float(current)) > abs(float(1*stdev+mean)) and abs(float(current)) < abs(float(2*stdev+mean)):
            watch.append(stock)
            watch_pct.append(current)
            watch_mean.append(mean)
            watch_std.append(stdev)
            
        elif abs(float(current)) > abs(float(2*stdev+mean)) and abs(float(current)) < abs(float(3*stdev+mean)):
            def_watch.append(stock)
            def_watch_pct.append(current)
            def_watch_mean.append(mean)
            def_watch_std.append(stdev)
        
        elif abs(float(current)) > abs(float(3*stdev+mean)):
            must_watch.append(stock)
            must_watch_pct.append(current)
            must_watch_mean.append(mean)
            must_watch_std.append(stdev)
        else:
            pass
    except:
        pass

try:
    print ('Watch:')
    df1 = pd.DataFrame(list(zip(watch, watch_pct, watch_mean, watch_std)), columns =['Company', 'Current', 'Mean', 'Stdev'])
    df1 = df1.set_index('Company')

    for n in df1['Current'].tolist():
        if n < 0:
            df1['First Band'] = -1*df1['Stdev']+df1['Mean']
            df1['Second Band'] = -2*df1['Stdev']+df1['Mean']
            df1['Third Band'] = -3*df1['Stdev']+df1['Mean']
            df1['pct'] = round((df1['Current'] - df1['Second Band']))
        else:
            df1['First Band'] = 1*df1['Stdev']+df1['Mean']
            df1['Second Band'] = 2*df1['Stdev']+df1['Mean']
            df1['Third Band'] = 3*df1['Stdev']+df1['Mean']
            df1['pct'] = round((df1['Current'] - df1['First Band']))
    print (df1)
except:
    pass

try:
    print ('\n')
    print ('Def Watch:')
    df2 = pd.DataFrame(list(zip(def_watch, def_watch_pct, def_watch_mean, def_watch_std)), columns =['Company', 'Current', 'Mean', 'Stdev'])
    df2 = df2.set_index('Company')
    
    for n in df2['Current'].tolist():
        if n < 0:
            df2['First Band'] = -1*df2['Stdev']+df2['Mean']
            df2['Second Band'] = -2*df2['Stdev']+df2['Mean']
            df2['Third Band'] = -3*df2['Stdev']+df2['Mean']
            df2['pct'] = round((df2['Current'] - df2['Second Band']))
        else:
            df2['First Band'] = 1*df2['Stdev']+df2['Mean']
            df2['Second Band'] = 2*df2['Stdev']+df2['Mean']
            df2['Third Band'] = 3*df2['Stdev']+df2['Mean']
            df2['pct'] = round((df2['Current'] - df2['Second Band']))
    print (df2)
except:
    pass

try:
    print ('\n')
    print ('Must Watch:')
    df3 = pd.DataFrame(list(zip(must_watch, must_watch_pct, must_watch_mean, must_watch_std)), columns =['Company', 'Current', 'Mean', 'Stdev'])
    df3 = df3.set_index('Company')
    
    for n in df3['Current'].tolist():
        if n < 0:
            df3['First Band'] = -1*df3['Stdev']+df3['Mean']
            df3['Second Band'] = -2*df3['Stdev']+df3['Mean']
            df3['Third Band'] = -3*df3['Stdev']+df3['Mean']
            df3['pct'] = round((df3['Current'] - df3['Third Band']))
        else:
            df3['First Band'] = 1*df3['Stdev']+df3['Mean']
            df3['Second Band'] = 2*df3['Stdev']+df3['Mean']
            df3['Third Band'] = 3*df3['Stdev']+df3['Mean']
            df3['pct'] = round((df3['Current'] - df3['Third Band']))
    print (df3)
except:
    pass

try:
    df1.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/strategy/extended-stocks/watch/{today}.csv')
    df2.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/strategy/extended-stocks/def_watch/{today}.csv')
    df3.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/strategy/extended-stocks/must_watch/{today}.csv')
except Exception as e:
    print (e)
