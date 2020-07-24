# imports
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd

# list all stocks
url = 'ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt'
df = pd.read_csv(url, sep = "|")

def lookup_fn(df, key_row, key_col):
    try:
        return df.iloc[key_row][key_col]
    except IndexError:
        return 0

movementlist = []
for stock in df['Symbol'].tolist()[:5]:
    # get history
    thestock = yf.Ticker(stock)
    hist = thestock.history(period="5d")
    # print(stock)
    low = float(10000)
    high = float(0)
    # print(thestock.info)
    
    for day in hist.itertuples(index=True, name='Pandas'):
        if day.Low < low:
            low = day.Low
        if high < day.High:
            high = day.High
  
    deltapercent = 100 * (high - low)/low
    Open = lookup_fn(hist, 0, "Open")
  
  # some error handling: 
    if len(hist >=5):
        Close = lookup_fn(hist, 4, "Close")
    else :
        Close = Open
    if(Open == 0):
        deltaprice = 0
    else:
        deltaprice = 100 * (Close - Open) / Open
    
    print(stock+" "+str(deltapercent)+ " "+ str(deltaprice))
    pair = [stock, deltapercent, deltaprice]
    movementlist.append(pair)
  
for entry in movementlist:
    if entry[1] > float(100):
        print(entry)

# High risers:
def lookup_stockinfo(thestock):
    try:
        return thestock.info
    except IndexError:
        return 0

cutoff = float(80)

for entry in movementlist:
    if entry[2] > cutoff:
        print("\n"+ str(entry))
        thestock = yf.Ticker(str(entry[0]))
        
        if entry[0]=='HJLIW':
            print("no info")   
            
        else:
            a = lookup_stockinfo(thestock)
            
            if a == 0 or a == None or a == "":
                print("no info")     

            else:
                print(a)
                print('Up '+ str(entry[2]) + "%")
                print(str(a['sector']))
                print(str(a['longBusinessSummary']))
                print("year high "+ str(a['fiftyTwoWeekHigh']))