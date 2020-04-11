import datetime
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from pandas import ExcelWriter

yf.pdr_override()
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

#root = Tk()
#ftypes = [(".xlsm","*.xlsx",".xls")]
#ttl  = "Title"
#dir1 = 'C:\\'
#filePath = askopenfilename(filetypes = ftypes, initialdir = dir1, title = ttl)
filePath = r"/Users/shashank/Downloads/Code/"

stocklist = pd.read_excel(r"/Users/shashank/Downloads/Code/Stocks.xlsx")

exportList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])

for i in stocklist.index:
    stock = str(stocklist["Symbol"][i])
    RS_Rating = stocklist["RS Rating"][i]

    try:
        df = pdr.get_data_yahoo(stock, start_date, end_date)

        smaUsed = [50, 150, 200]
        for x in smaUsed:
            sma = x
            df["SMA_"+str(sma)] = round(df.iloc[:,
                                                4].rolling(window=sma).mean(), 2)

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
            cond_1 = True
        else:
            cond_1 = False
        # Condition 2: 150 SMA and > 200 SMA
        if(moving_average_150 > moving_average_200):
            cond_2 = True
        else:
            cond_2 = False
        # Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
        if(moving_average_200 > moving_average_200_20):
            cond_3 = True
        else:
            cond_3 = False
        # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
        if(moving_average_50 > moving_average_150 > moving_average_200):
            #print("Condition 4 met")
            cond_4 = True
        else:
            #print("Condition 4 not met")
            cond_4 = False
        # Condition 5: Current Price > 50 SMA
        if(currentClose > moving_average_50):
            cond_5 = True
        else:
            cond_5 = False
        # Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
        if(currentClose >= (1.3*low_of_52week)):
            cond_6 = True
        else:
            cond_6 = False
        # Condition 7: Current Price is within 25% of 52 week high
        if(currentClose >= (.75*high_of_52week)):
            cond_7 = True
        else:
            cond_7 = False
        # Condition 8: IBD RS rating >70 and the higher the better
        if(RS_Rating > 70):
            cond_8 = True
        else:
            cond_8 = False

        if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7 and cond_8):
            exportList = exportList.append({'Stock': stock, "RS_Rating": RS_Rating, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)
            print (stock + " made the requirements")
    except Exception:
        print("No data on "+stock)

print(exportList)

newFile = os.path.dirname(filePath)+"/ScreenOutput.xlsx"
writer = ExcelWriter(newFile)
exportList.to_excel(writer, "Sheet1")
writer.save()