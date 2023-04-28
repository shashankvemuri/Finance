# Import Dependencies
import datetime as dt
import pandas as pd
from pandas_datareader import DataReader
import yahoo_fin.stock_info as si
import time

# Get today's date
now = dt.date.today()

# Get a list of S&P 500 tickers
tickers = si.tickers_sp500()

# Replace periods with dashes in ticker names
tickers = [item.replace(".", "-") for item in tickers]

# Initialize list and add today's date to it
mylist = []
today = dt.date.today()
mylist.append(today)

# Get today's date from the list
today = mylist[0]

# Initialize empty lists
diff_5 = []
diff_5_tickers = []

# Loop through each ticker
for ticker in tickers:
    try:
        # Print ticker symbol
        print (ticker+':')
        
        # Get the current price of the stock
        price = si.get_live_price(ticker)
        
        # Read in historical stock data for the current ticker
        df = pd.read_csv(f'/Users/shashank/Documents/Code/Python/Outputs/S&P500/{ticker}.csv', index_col=0)
        df.index = pd.to_datetime(df.index)
        
        # Remove rows with volume less than 1000
        df.drop(df[df["Volume"]<1000].index, inplace=True)
        
        # Get the maximum high price for each month
        dfmonth=df.groupby(pd.Grouper(freq="M"))["High"].max()
        
        # Initialize variables
        glDate=0
        lastGLV=0
        currentDate=""
        curentGLV=0
        counter=0
        
        # Loop through each month's high price
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
        
        # Check if the last green line value was found
        if lastGLV==0:
            message=ticker+" has not formed a green line yet"
        
        else:
            # Calculate the difference between the last green line value and the current price
            if lastGLV < 1.05 * price and lastGLV > .95*price:
                diff = lastGLV/price
                diff = round(diff - 1, 3)
                diff = diff*100
                
                # Print the difference and the last green line date
                print (f"\n{ticker.upper()}'s last green line value ({round(lastGLV, 2)}) is {round(diff,1)}% greater than it's current price ({round(price, 2)})")
                message=("Last Green Line: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
    
                # Append the ticker symbol and the difference to the lists
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

# Create Dataframe and Print
df = pd.DataFrame(list(zip(diff_5_tickers, diff_5)), columns =['Company', 'GLV % Difference'])
df = df.reindex(df['GLV % Difference'].abs().sort_values().index)
print ('Watchlist: ')
print (df)
