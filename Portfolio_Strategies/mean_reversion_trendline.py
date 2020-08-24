# Use a 200MA as a trend filter (above the moving average is an uptrend)
# Enter long (on next day open) when the 2-day Cumulative RSI value is less than 33
# Exit (on next day open) when 2-day RSI is above 20

import datetime
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from pandas import ExcelWriter
import time
import talib

yf.pdr_override()

num_of_years = 10
start = datetime.datetime.now() - datetime.timedelta(int(365.25 * num_of_years))
end = datetime.datetime.now() 

# Make the ticker symbols readable by Yahoo Finance
stocklist = pd.read_pickle('../spxTickers.pickle')
stocklist = [item.replace(".", "-") for item in stocklist]

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

final = []
index = []
n = -1

exportList = pd.DataFrame(columns=['Stock', "RSI", "200 Day MA"])
otherList = pd.DataFrame(columns=['Stock', "RSI", "200 Day MA", "Failed"])

for stock in stocklist[:5]:
    #n += 1
    time.sleep(1.5)
    
    print ("\npulling {}".format(stock))
    # rsi value
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    
    df = pdr.get_data_yahoo(stock, start=start_date, end=end_date)

    try:
        df["SMA_200"] = round(df.iloc[:,4].rolling(window=200).mean(), 2)
        currentClose = df["Adj Close"][-1]
        moving_average_200 = df["SMA_200"][-1]
        
        df["rsi"] = talib.RSI(df["Close"])
        RSI = df["rsi"].tail(14).mean()
        
        two_day = (df.rsi[-1] + df.rsi[-2])/2
        
        # Condition 1: Current Price > 200 SMA
        if(currentClose >  moving_average_200):
            condition_1 = True
        else:
            condition_1 = False

        # Condition 2: 2-day Cumulative RSI value is less than 33
        if(two_day < 33):
            condition_2 = True
        else:
            condition_2 = False

        if(condition_1 and condition_2):
            exportList = exportList.append({'Stock': stock, "RSI": RSI, "200 Day MA": moving_average_200}, ignore_index=True)
            #print (stock + " made the requirements")
        
        else:
            conditions = {'condition_1': condition_1, 'condition_2': condition_2}
            
            false = []
            for condition in conditions: 
                if conditions[condition] == False: 
                    false.append(condition)
                else:
                    pass
                
            print (stock + " did not make the requirements because of: ")        
            for value in false: 
                print (value)
            
            otherList = otherList.append({'Stock': stock, "RSI": RSI, "200 Day MA": moving_average_200,  "Failed": false}, ignore_index=True)

    except Exception as e:
        pass
        #print (e)
        #print("No data on "+stock)

#print(exportList)
writer = ExcelWriter('/Users/shashank/Documents/Code/Python/Outputs/trading-strat/Export-Output_{}.xlsx'.format(today))
exportList.to_excel(writer, "Sheet1")
writer.save()

writer = ExcelWriter('/Users/shashank/Documents/Code/Python/Outputs/trading-strat/Other-Output_{}.xlsx'.format(today))
otherList.to_excel(writer, "Sheet1")
writer.save()