# Import dependencies
import datetime as dt
import pandas as pd
from pandas_datareader import DataReader
import matplotlib.pyplot as plt
from pylab import rcParams 
import yahoo_fin.stock_info as si

# Set the start date for historical data
start = dt.datetime(1980,12,1)
# Set the end date for historical data to today's date
now = dt.datetime.now()

# Ask user to input a stock ticker
stock = input('Enter a ticker: ')

# Continue asking user for a stock ticker until they enter 'quit'
while stock != 'quit':
    
    # Get the current stock price
    price = si.get_live_price(stock)
    
    # Get the historical stock data
    df = DataReader(stock, 'yahoo', start, now)
    
    # Remove rows where volume is less than 1000
    df.drop(df[df["Volume"]<1000].index, inplace=True)
    
    # Get the maximum high for each month
    dfmonth = df.groupby(pd.Grouper(freq="M"))["High"].max()
    
    # Initialize variables for green line analysis
    glDate = 0
    lastGLV = 0
    currentDate = ""
    curentGLV = 0
    counter = 0
    
    # Loop through the monthly high data to find the last green line value
    for index, value in dfmonth.items():
        if value > curentGLV:
            curentGLV = value
            currentDate = index
            counter = 0
        if value < curentGLV:
            counter += 1
            # If there are 3 consecutive months with lower highs than the current green line value,
            # and it's not the current month or year, then the last green line value has been found
            if counter == 3 and ((index.month != now.month) or (index.year != now.year)):
                if curentGLV != lastGLV:
                    print(curentGLV)
                glDate = currentDate
                lastGLV = curentGLV
                counter = 0
    
    # Determine the message to display based on the last green line value and the current price
    if lastGLV == 0:
        message = f"{stock} has not formed a green line yet"
    else:
        if lastGLV > 1.15 * price: 
            # If the current price is more than 15% lower than the last green line value, display a message
            # showing the percentage difference between the last green line value and the current price
            diff = price/lastGLV
            diff = round(diff - 1, 3)
            diff = diff*100
            message = f"\n{stock.upper()}'s current price ({round(price, 2)}) is {diff}% away from its last green line value ({round(lastGLV, 2)})"
        else: 
            if lastGLV < 1.05 * price:
                # If the current price is more than 5% higher than the last green line value, display a message
                # showing the percentage difference between the last green line value and the current price, as well as
                # a plot of the stock's close price with the last green line value highlighted
                diff = lastGLV/price
                diff = round(diff - 1, 3)
                diff = diff*100
                print(f"\n{stock.upper()}'s last green line value ({round(lastGLV, 2)}) is {diff}% greater than it's current price ({round(price, 2)})")
                message=("Last Green Line: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
              
                fig, ax = plt.subplots()
                rcParams['figure.figsize'] = 15, 10
                ax.plot(df['Close'].tail(120))
                ax.axhline(lastGLV, color='g')
                plt.title(f"{stock.upper()}'s Close Price Green Line Test")
                plt.xlabel('Dates')
                plt.ylabel('Close Price')
                plt.show()
            
            else: 
                message=("Last Green Line: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
              
                fig, ax = plt.subplots()
                rcParams['figure.figsize'] = 15, 10
                ax.plot(df['Close'])
                ax.axhline(lastGLV, color='g')
                plt.title(f"{stock.upper()}'s Close Price Green Line Test")
                plt.xlabel('Dates')
                plt.ylabel('Close Price')
                plt.show()
    
    print(message)
    stock = input('enter another ticker: ')