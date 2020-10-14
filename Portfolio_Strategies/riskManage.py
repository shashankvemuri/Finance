import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import statistics
import time

yf.pdr_override()
now = dt.datetime.now()
start =dt.datetime(2019,1,1)

smaUsed=[50,200]
emaUsed=[21]

stock = input('Enter a ticker: ')
position = input('Buy or Short? ')
AvgGain= int(input('Enter Your Average Gain: '))
AvgLoss= int(input('Enter Your Average Loss: '))

if position.lower() == 'buy':
    df = pdr.get_data_yahoo(stock, start, now)
    close=df["Adj Close"][-1]
    maxStop=close*((100-AvgLoss)/100)
    Target1R=round(close*((100+AvgGain)/100),2)
    Target2R=round(close*(((100+(2*AvgGain))/100)),2)
    Target3R=round(close*(((100+(3*AvgGain))/100)),2)
    
    for x in smaUsed:
        sma=x
        df["SMA_"+str(sma)]=round(df.iloc[:,4].rolling(window=sma).mean(),2)
    for x in emaUsed:
    	ema=x
    	df['EMA_'+str(ema)] = round(df.iloc[:,4].ewm(span=ema,adjust=False).mean(),2)
       
    sma50=round(df["SMA_50"][-1],2)
    sma200=round(df["SMA_200"][-1],2)
    ema21=round(df["EMA_21"][-1],2)
    low5=round(min(df["Low"].tail(5)),2)
       
    pf50=round(((close/sma50)-1)*100,2)
    check50=df["SMA_50"][-1]>maxStop
    pf200=round(((close/sma200)-1)*100,2)
    check200=((close/df["SMA_200"][-1])-1)*100>100
    pf21=round(((close/ema21)-1)*100,2)
    check21=df["EMA_21"][-1]>maxStop 
    pfl=round(((close/low5)-1)*100,2)
    checkl=pfl>maxStop 
       
    print()
    print("Current Stock: "+stock+" Price: "+str(round(close,2)))
    print("21 EMA: "+str(ema21)+ " | 50 SMA: "+str(sma50)+ " | 200 SMA: "+str(sma200)+ " | 5 day Low: "+str(low5))
    print("-------------------------------------------------")
    print("Max Stop: "+str(round(maxStop,2)))
    print("Price Targets:") 
    print("1R: "+str(Target1R))
    print("2R: "+str(Target2R))
    print("3R: "+str(Target3R))
    print("From 5 Day Low "+ str(pfl)+ "% -Within Max Stop: "+str(checkl))
    print("From 21 day EMA "+ str(pf21)+ "% -Within Max Stop: "+str(check21))
    print("From 50 day SMA "+ str(pf50)+ "% -Within Max Stop: "+str(check50))
    print("From 200 Day SMA "+ str(pf200)+ "% -In Danger Zone (Over 100% from 200 SMA): "+str(check200))
    print()

elif position.lower() == 'short':
    df = pdr.get_data_yahoo(stock, start, now)
    close=df["Adj Close"][-1]
    maxStop=close*((100+AvgLoss)/100)
    Target3R=round(close*(((100-(3*AvgGain))/100)),2)
    Target2R=round(close*(((100-(2*AvgGain))/100)),2)
    Target1R=round(close*((100-AvgGain)/100),2)
    
    for x in smaUsed:
        sma=x
        df["SMA_"+str(sma)]=round(df.iloc[:,4].rolling(window=sma).mean(),2)
    for x in emaUsed:
    	ema=x
    	df['EMA_'+str(ema)] = round(df.iloc[:,4].ewm(span=ema,adjust=False).mean(),2)
       
    sma50=round(df["SMA_50"][-1],2)
    sma200=round(df["SMA_200"][-1],2)
    ema21=round(df["EMA_21"][-1],2)
    low5=round(min(df["Low"].tail(5)),2)
       
    pf50=round(((close/sma50)-1)*100,2)
    check50=df["SMA_50"][-1]>maxStop
    pf200=round(((close/sma200)-1)*100,2)
    check200=((close/df["SMA_200"][-1])-1)*100>100
    pf21=round(((close/ema21)-1)*100,2)
    check21=df["EMA_21"][-1]>maxStop 
    pfl=round(((close/low5)-1)*100,2)
    checkl=pfl>maxStop 
       
    print()
    print("Current Stock: "+stock+" Price: "+str(round(close,2)))
    print("21 EMA: "+str(ema21)+ " | 50 SMA: "+str(sma50)+ " | 200 SMA: "+str(sma200)+ " | 5 day Low: "+str(low5))
    print("-------------------------------------------------")
    print("Max Stop: "+str(round(maxStop,2)))
    print("Price Targets:") 
    print("1R: "+str(Target1R))
    print("2R: "+str(Target2R))
    print("3R: "+str(Target3R))
    print("From 5 Day Low "+ str(pfl)+ "% -Within Max Stop: "+str(checkl))
    print("From 21 day EMA "+ str(pf21)+ "% -Within Max Stop: "+str(check21))
    print("From 50 day SMA "+ str(pf50)+ "% -Within Max Stop: "+str(check50))
    print("From 200 Day SMA "+ str(pf200)+ "% -In Danger Zone (Over 100% from 200 SMA): "+str(check200))
    print()