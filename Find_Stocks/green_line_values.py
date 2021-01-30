import datetime as dt
import pandas as pd
from pandas_datareader import DataReader
import yahoo_fin.stock_info as si
import time

now = dt.date.today()

tickers = si.tickers_sp500()
tickers = [item.replace(".", "-") for item in tickers]

mylist = []
today = dt.date.today()
mylist.append(today)
today = mylist[0]

diff_5 = []
diff_5_tickers = []

for ticker in tickers:
    try:
        print (ticker+':')
        price = si.get_live_price(ticker)
        
        df = pd.read_csv(f'/Users/shashank/Documents/Code/Python/Outputs/S&P500/{ticker}.csv', index_col=0)
        df.index = pd.to_datetime(df.index)
        df.drop(df[df["Volume"]<1000].index, inplace=True)
        
        dfmonth=df.groupby(pd.Grouper(freq="M"))["High"].max()
        
        glDate=0
        lastGLV=0
        currentDate=""
        curentGLV=0
        for index, value in dfmonth.items():
          if value > curentGLV:
            curentGLV=value
            currentDate=index
            counter=0
          if value < curentGLV:
            counter=counter+1
        
            if counter==3 and ((index.month != now.month) or (index.year != now.year)):
                if curentGLV != lastGLV:
                    pass
                glDate=currentDate
                lastGLV=curentGLV
                counter=0
        
        if lastGLV==0:
            message=ticker+" has not formed a green line yet"
        
        else:
            if lastGLV < 1.05 * price and lastGLV > .95*price:
                diff = lastGLV/price
                diff = round(diff - 1, 3)
                diff = diff*100
                
                print (f"\n{ticker.upper()}'s last green line value ({round(lastGLV, 2)}) is {round(diff,1)}% greater than it's current price ({round(price, 2)})")
                message=("Last Green Line: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
    
                diff_5_tickers.append(ticker)
                diff_5.append(diff)
            
            else: 
                diff = lastGLV/price
                diff = round(diff - 1, 3)
                diff = diff*100
                message=(f"Last Green Line for {ticker}: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
    
        print(message)
        print('-'*100)
    except Exception as e: 
        print (e)
        pass
    
df = pd.DataFrame(list(zip(diff_5_tickers, diff_5)), columns =['Company', 'Difference'])
df = df.reindex(df.Difference.abs().sort_values().index)

df.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/strategy/glv-stocks/{today}.csv', index=False)

print ('Watchlist: ')
print (df)
