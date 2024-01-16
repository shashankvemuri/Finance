import datetime as dt
import pandas as pd
import pandas_datareader.data as pdr
import matplotlib.pyplot as plt
from pylab import rcParams 
import yfinance as yf
yf.pdr_override()

# Set the start and end dates for historical data retrieval
start = dt.datetime(1980, 12, 1)
now = dt.datetime.now()

# Ask the user to input a stock ticker, loop continues until 'quit' is entered
stock = input('Enter a ticker: ')
while stock != 'quit':
    # Fetch historical stock data
    df = pdr.get_data_yahoo(stock, start, now)
    price = df['Adj Close'][-1]
    
    # Filter out days with very low trading volume
    df.drop(df[df["Volume"] < 1000].index, inplace=True)
    
    # Get the monthly maximum of the 'High' column
    df_month = df.groupby(pd.Grouper(freq="M"))["High"].max()
    
    # Initialize variables for the green line analysis
    glDate, lastGLV, currentDate, currentGLV, counter = 0, 0, "", 0, 0
    
    # Loop through monthly highs to determine the most recent green line value
    for index, value in df_month.items():
        if value > currentGLV:
            currentGLV = value
            currentDate = index
            counter = 0
        if value < currentGLV:
            counter += 1
            if counter == 3 and ((index.month != now.month) or (index.year != now.year)):
                if currentGLV != lastGLV:
                    print(currentGLV)
                glDate = currentDate
                lastGLV = currentGLV
                counter = 0

    # Determine the message to display based on green line value and current price
    if lastGLV == 0:
        message = f"{stock} has not formed a green line yet"
    else:
        diff = price/lastGLV - 1
        diff = round(diff * 100, 3)
        if lastGLV > 1.15 * price:
            message = f"\n{stock.upper()}'s current price ({round(price, 2)}) is {diff}% away from its last green line value ({round(lastGLV, 2)})"
        else: 
            if lastGLV < 1.05 * price:
                print(f"\n{stock.upper()}'s last green line value ({round(lastGLV, 2)}) is {diff}% greater than its current price ({round(price, 2)})")
                message = ("Last Green Line: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
              
                fig, ax = plt.subplots()
                rcParams['figure.figsize'] = 15, 10
                ax.plot(df['Close'].tail(120))
                ax.axhline(lastGLV, color='g')
                plt.title(f"{stock.upper()}'s Close Price Green Line Test")
                plt.xlabel('Dates')
                plt.ylabel('Close Price')
                plt.show()
            else: 
                message = ("Last Green Line: "+str(round(lastGLV, 2))+" on "+str(glDate.strftime('%Y-%m-%d')))
                fig, ax = plt.subplots()
                rcParams['figure.figsize'] = 15, 10
                ax.plot(df['Close'])
                ax.axhline(lastGLV, color='g')
                plt.title(f"{stock.upper()}'s Close Price Green Line Test")
                plt.xlabel('Dates')
                plt.ylabel('Close Price')
                plt.show()
    
    print(message)
    stock = input('Enter another ticker: ')