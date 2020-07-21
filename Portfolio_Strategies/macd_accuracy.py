# Necessary Libraries
import yfinance as yf, pandas as pd
import shutil
import os
import time
import glob
import numpy as np
import requests
from get_all_tickers import get_tickers as gt
from statistics import mean
from yahoo_fin import stock_info as si

# tickers = gt.get_tickers_filtered(mktcap_min=150000, mktcap_max=10000000)
tickers = si.tickers_sp500()

print("The amount of stocks chosen to observe: " + str(len(tickers)))

shutil.rmtree("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/Stocks/")
os.mkdir("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/Stocks/")

Amount_of_API_Calls = 0
Stock_Failure = 0
Stocks_Not_Imported = 0
i = 0

while (i < len(tickers)) and (Amount_of_API_Calls < 1800):
    try:
        print("Iteration = " + str(i))
        stock = tickers[i]
        temp = yf.Ticker(str(stock))
        Hist_data = temp.history(period="max")
        Hist_data.to_csv("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/Stocks/"+stock+".csv")
        time.sleep(2)
        Amount_of_API_Calls += 1 
        Stock_Failure = 0
        i += 1
    except ValueError:
        print("Yahoo Finance Backend Error, Attempting to Fix")
        if Stock_Failure > 5:
            i+=1
            Stocks_Not_Imported += 1
        Amount_of_API_Calls += 1
        Stock_Failure += 1

    except requests.exceptions.SSLError as e:
        print("Yahoo Finance Backend Error, Attempting to Fix SSL")
        if Stock_Failure > 5:
            i+=1
            Stocks_Not_Imported += 1
        Amount_of_API_Calls += 1
        Stock_Failure += 1
print("The amount of stocks we successfully imported: " + str(i - Stocks_Not_Imported))

list_files = (glob.glob("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/Stocks/*.csv"))
Compare_Stocks = pd.DataFrame(columns=["Company", "Days_Observed", "Crosses", "True_Positive", "False_Positive", "True_Negative", "False_Negative", "Sensitivity", 
"Specificity", "Accuracy", "TPR", "FPR"])

count = 0
for stock in list_files:
    Hist_data = pd.read_csv(stock)
    Company = ((os.path.basename(stock)).split(".csv")[0])
    Days_Observed = 0
    Crosses = 0
    True_Positive = 0
    False_Positive = 0
    True_Negative = 0
    False_Negative = 0
    Sensitivity = 0
    Specificity = 0
    Accuracy = 0

    prices = []
    c = 0

    while c < len(Hist_data):
        if Hist_data.iloc[c,4] > float(2.00):
            prices.append(Hist_data.iloc[c,4])
        c += 1
    prices_df = pd.DataFrame(prices)

    day12 = prices_df.ewm(span=12).mean()  #
    day26 = prices_df.ewm(span=26).mean()
    macd = []
    counter=0
    while counter < (len(day12)):
        macd.append(day12.iloc[counter,0] - day26.iloc[counter,0])
        counter += 1
    macd_df = pd.DataFrame(macd)
    signal_df = macd_df.ewm(span=9).mean()
    signal = signal_df.values.tolist()

    Day = 1
    while Day < len(macd)-5:
        Prev_Day = Day-1

        Avg_Closing_Next_Days = (prices[Day+1] + prices[Day+2] + prices[Day+3])/3
        Days_Observed += 1
        if ((signal[Prev_Day] > macd[Prev_Day]) and (signal[Day] <= macd[Day])):
            Crosses += 1
            if (prices[Day] < Avg_Closing_Next_Days):
                True_Positive += 1
            else:
                False_Negative += 1

        if ((signal[Prev_Day] < macd[Prev_Day]) and (signal[Day] >= macd[Day])):
            Crosses += 1
            if (prices[Day] > Avg_Closing_Next_Days):
                True_Negative += 1
            else:
                False_Positive += 1
        Day += 1
    try:
        Sensitivity = (True_Positive / (True_Positive + False_Negative))
    except ZeroDivisionError:
        Sensitivity = 0
    try:
        Specificity = (True_Negative / (True_Negative + False_Positive))
    except ZeroDivisionError:
        Specificity
    try:
        Accuracy = (True_Positive + True_Negative) / (True_Negative + True_Positive + False_Positive + False_Negative)
    except ZeroDivisionError:
        Accuracy = 0
    TPR = Sensitivity
    FPR = 1 - Specificity

    add_row = {'Company' : Company, 'Days_Observed' : Days_Observed, 'Crosses' : Crosses, 'True_Positive' : True_Positive, 'False_Positive' : False_Positive, 
    'True_Negative' : True_Negative, 'False_Negative' : False_Negative, 'Sensitivity' : Sensitivity, 'Specificity' : Specificity, 'Accuracy' : Accuracy, 'TPR' : TPR, 'FPR' : FPR} 
    Compare_Stocks = Compare_Stocks.append(add_row, ignore_index = True)
    count += 1

Compare_Stocks.to_csv("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/All_Stocks.csv", index = False)
Compare_Stocks = pd.read_csv("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/All_Stocks.csv")

Not_Enough_Records = []  
Row = 0

while Row < (len(Compare_Stocks)):
    if Compare_Stocks.iloc[Row, 2] < 50:
        Not_Enough_Records.append(Row)  
    Row += 1

Compare_Stocks = Compare_Stocks.drop(Not_Enough_Records)
Avg_Accuracy = []
i = 0

while i < (len(Compare_Stocks)):
    Avg_Accuracy.append(Compare_Stocks.iloc[i,9])
    i += 1

df = Compare_Stocks[['Company','Days_Observed', 'Crosses', 'True_Positive', 'False_Positive', 'True_Negative', 'False_Negative', 'Sensitivity', 'Specificity', 'TPR', 'FPR', 'Accuracy']]
df["Companies_Ranked"] = df["Accuracy"].rank(ascending = False)

df.sort_values("Accuracy", inplace = True, ascending = False)
df.to_csv("/Users/shashank/Documents/Code/Python/Outputs/macd_accuracy/SMA_Analysis/5_Day_Avg_26_12_MACD.csv", index = False)

print("The average accuracy of all stocks observed: " + str(mean(Avg_Accuracy)))