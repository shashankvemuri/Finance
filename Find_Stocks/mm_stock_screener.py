import datetime
import pandas as pd
from pandas_datareader import DataReader
import yfinance as yf
from pandas import ExcelWriter
import requests
from yahoo_fin import stock_info as si
import time
import bs4 as bs
import pickle
import talib

def save_spx_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.find_all('td') [0].text.strip()
        tickers.append(ticker)
        
    with open('spxTickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)       
    return tickers
        
stocklist = save_spx_tickers()

# Make the ticker symbols readable by Yahoo Finance
stocklist = [item.replace(".", "-") for item in stocklist]

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

final = []
index = []
n = -1

exportList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])
otherList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High", "Failed"])

for stock in stocklist:
    #n += 1
    time.sleep(1.5)
    
    print ("\npulling {}".format(stock))
    # rsi value
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    
    df = DataReader(stock, 'yahoo', start=start_date, end=end_date)
    
    df["rsi"] = talib.RSI(df["Close"])
    
    RS_Rating = df["rsi"].tail(14).mean()

    try:
        smaUsed = [50, 150, 200]
        for x in smaUsed:
            sma = x
            df["SMA_"+str(sma)] = round(df.iloc[:,4].rolling(window=sma).mean(), 2)

        currentClose = df["Adj Close"][-1]
        moving_average_50 = df["SMA_50"][-1]
        moving_average_150 = df["SMA_150"][-1]
        moving_average_200 = df["SMA_200"][-1]
        low_of_52week = min(df["Adj Close"][-260:])
        high_of_52week = max(df["Adj Close"][-260:])
        
        try:
            moving_average_200_20 = df["SMA_200"][-20]

        except Exception:
            moving_average_200_20 = 0

        # Condition 1: Current Price > 150 SMA and > 200 SMA
        if(currentClose > moving_average_150 > moving_average_200):
            condition_1 = True
        else:
            condition_1 = False
        # Condition 2: 150 SMA and > 200 SMA
        if(moving_average_150 > moving_average_200):
            condition_2 = True
        else:
            condition_2 = False
        # Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
        if(moving_average_200 > moving_average_200_20):
            condition_3 = True
        else:
            condition_3 = False
        # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
        if(moving_average_50 > moving_average_150 > moving_average_200):
            #print("Condition 4 met")
            condition_4 = True
        else:
            #print("Condition 4 not met")
            condition_4 = False
        # Condition 5: Current Price > 50 SMA
        if(currentClose > moving_average_50):
            condition_5 = True
        else:
            condition_5 = False
        # Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
        if(currentClose >= (1.3*low_of_52week)):
            condition_6 = True
        else:
            condition_6 = False
        # Condition 7: Current Price is within 25% of 52 week high
        if(currentClose >= (.75*high_of_52week)):
            condition_7 = True
        else:
            condition_7 = False
        # Condition 8: IBD RS rating < 30 and the higher the better
        if(RS_Rating < 30):
            condition_8 = True
        else:
            condition_8 = False

        if(condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7 and condition_8):            
            exportList = exportList.append({'Stock': stock, "RS_Rating": RS_Rating, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)
            #print (stock + " made the requirements")
        
        else:
            conditions = {'condition_1': condition_1, 'condition_2': condition_2, 'condition_3': condition_3, 'condition_4': condition_4, 'condition_5': condition_5, 'condition_6': condition_6, 'condition_7': condition_7, 'condition_8': condition_8}
            
            false = []
            for condition in conditions: 
                if conditions[condition] == False: 
                    false.append(condition)
                else:
                    pass
                
            print (stock + " did not make the requirements because of: ")        
            for value in false: 
                print (value)
            
            otherList = otherList.append({'Stock': stock, "RS_Rating": RS_Rating, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week, "Failed": false}, ignore_index=True)

    except Exception as e:
        pass
        #print (e)
        #print("No data on "+stock)

#print(exportList)
writer = ExcelWriter('/Users/shashank/Documents/GitHub/Code/mm-screener-output/Export-Output_{}.xlsx'.format(today))
exportList.to_excel(writer, "Sheet1")
writer.save()

writer = ExcelWriter('/Users/shashank/Documents/GitHub/Code/mm-screener-output/Other-Output_{}.xlsx'.format(today))
otherList.to_excel(writer, "Sheet1")
writer.save()
