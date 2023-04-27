# Import required libraries
import datetime
import time
import pandas as pd
import talib
from pandas_datareader import data as pdr
from pandas import ExcelWriter
import yfinance as yf

# Override yfinance module to fix issues with pandas_datareader
yf.pdr_override()

# Define the number of years to get data for and the start and end dates
num_of_years = 10
start = datetime.datetime.now() - datetime.timedelta(int(365.25 * num_of_years))
end = datetime.datetime.now()

# Load stock symbols from a pickle file
stocklist = pd.read_pickle('../spxTickers.pickle')

# Replace periods with hyphens in the stock symbols for Yahoo Finance compatibility
stocklist = [item.replace(".", "-") for item in stocklist]

# Initialize empty lists and variables
exportList = pd.DataFrame(columns=['Stock', "RSI", "200 Day MA"])
mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

# Loop through all stocks in the list
for stock in stocklist[:5]:
    # Sleep for 1.5 seconds to avoid hitting Yahoo Finance API rate limits
    time.sleep(1.5)

    print ("\npulling {}".format(stock))

    # Get data from Yahoo Finance API
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    df = pdr.get_data_yahoo(stock, start=start_date, end=end_date)

    try:
        # Calculate the 200-day moving average, current close price, and RSI values
        df["SMA_200"] = round(df.iloc[:,4].rolling(window=200).mean(), 2)
        currentClose = df["Adj Close"][-1]
        moving_average_200 = df["SMA_200"][-1]
        df["rsi"] = talib.RSI(df["Close"])
        RSI = df["rsi"].tail(14).mean()
        two_day = (df.rsi[-1] + df.rsi[-2])/2

        # Check if conditions for entering a long position are met
        condition_1 = currentClose >  moving_average_200
        condition_2 = two_day < 33

        if condition_1 and condition_2:
            # If conditions are met, add the stock to the export list
            exportList = exportList.append({'Stock': stock, "RSI": RSI, "200 Day MA": moving_average_200}, ignore_index=True)
            print (stock + " made the requirements")

    except Exception as e:
        # If there is an error getting data for the stock, skip it
        print (e)
        pass

# Save the export and other lists to separate Excel files
print(exportList)
writer = ExcelWriter('Export-Output_{}.xlsx'.format(today))
exportList.to_excel(writer, "Sheet1")
writer.save()