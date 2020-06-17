#import relevant libraries
import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import datetime as datetime
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
from pylab import rcParams

yf.pdr_override() 

#Choose smas
smasUsed=[10,30,50] 

start = dt.datetime(2020,1,1)- dt.timedelta(days=max(smasUsed)) 
now = dt.datetime.now() 
stock = input("Enter the stock symbol : ")

while stock != "quit": 
    
    prices = pdr.get_data_yahoo(stock, start, now)
    
    fig, ax1 = plt.subplots() 

    # Calculate moving averages
    for x in smasUsed: 
      sma=x
      prices['SMA_'+str(sma)] = prices.iloc[:,4].rolling(window=sma).mean()
    
    # Calculate Bollinger Bands
    BBperiod = 15
    stdev=2
    prices['SMA'+str(BBperiod)] = prices.iloc[:,4].rolling(window=BBperiod).mean() 
    prices['STDEV']=prices.iloc[:,4].rolling(window=BBperiod).std()
    prices['LowerBand']=prices['SMA'+str(BBperiod)]-(stdev*prices['STDEV'])
    prices['UpperBand']=prices['SMA'+str(BBperiod)]+(stdev*prices['STDEV'])
    prices["Date"]=mdates.date2num(prices.index)
    
    #Calculate 10.4.4 stochastic
    Period=10 
    K=4 
    D=4 
    
    prices["RolHigh"] = prices["High"].rolling(window=Period).max()
    prices["RolLow"] = prices["Low"].rolling(window=Period).min() 
    prices["stok"] = ((prices["Adj Close"]-prices["RolLow"])/(prices["RolHigh"]-prices["RolLow"]))*100
    prices["K"] = prices["stok"].rolling(window=K).mean() 
    prices["D"] = prices["K"].rolling(window=D).mean() 
    prices["GD"]=prices["High"] 
    
    ohlc = [] 
    
    prices=prices.iloc[max(smasUsed):]
    
    
    greenDotDate = [] 
    greenDot = [] 
    lastK = 0 
    lastD = 0 
    lastLow = 0 
    lastClose = 0 
    lastLowBB = 0 
    
    
    #Go through price history to create candlestics and GD+Blue dots
    for i in prices.index: 
      append_me = prices["Date"][i], prices["Open"][i], prices["High"][i], prices["Low"][i], prices["Adj Close"][i], prices["Volume"][i]
      ohlc.append(append_me)
    
      #Check for Green Dot
      if prices['K'][i]>prices['D'][i] and lastK<lastD and lastK <60:
    
        #plt.Circle((prices["Date"][i],prices["High"][i]),1) 
        #plt.bar(prices["Date"][i],1,1.1,bottom=prices["High"][i]*1.01,color='g')
        plt.plot(prices["Date"][i],prices["High"][i]+1, marker="o", ms=4, ls="", color='g') 
    
        greenDotDate.append(i) #store green dot date
        greenDot.append(prices["High"][i])  #store green dot value
    
      #Check for Lower Bollinger Band Bounce
      if ((lastLow<lastLowBB) or (prices['Low'][i]<prices['LowerBand'][i])) and (prices['Adj Close'][i]>lastClose and prices['Adj Close'][i]>prices['LowerBand'][i]) and lastK <60:  
        plt.plot(prices["Date"][i],prices["Low"][i]-1, marker="o", ms=4, ls="", color='b') 
     
      #store values
      lastK=prices['K'][i]
      lastD=prices['D'][i]
      lastLow=prices['Low'][i]
      lastClose=prices['Adj Close'][i]
      lastLowBB=prices['LowerBand'][i]
    
    #Plot moving averages and BBands
    for x in smasUsed: 
      sma=x
      prices['SMA_'+str(sma)].plot(label='close') 
    prices['UpperBand'].plot(label='close',color='lightgray') 
    prices['LowerBand'].plot(label='close', color='lightgray') 
    
    #plot candlesticks
    candlestick_ohlc(ax1, ohlc, width=.5, colorup='k', colordown='r', alpha=0.75)
    
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(8)) 
    plt.tick_params(axis='x', rotation=45)
    
    #Pivot Points
    pivots = []
    dates = []  
    counter = 0
    lastPivot = 0 
    
    Range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dateRange = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in prices.index: 
      currentMax=max(Range, default=0) 
      value=round(prices["High"][i],2) 
    
      Range=Range[1:9] 
      Range.append(value) 
      dateRange=dateRange[1:9]  
      dateRange.append(i)
    
      if currentMax == max(Range, default=0):
        counter+=1 
      else:
        counter = 0 
      if counter == 5: 
        lastPivot = currentMax 
        dateloc = Range.index(lastPivot) 
        lastDate = dateRange[dateloc]
        pivots.append(currentMax)
        dates.append(lastDate)
    print()
    
    timeD = dt.timedelta(days=30) 
    
    for index in range(len(pivots)):
    
      #print(str(pivots[index])+": "+str(dates[index])) #Prints Pivot, Date couple
      plt.plot_date([dates[index]-(timeD*.075), dates[index]+timeD], 
                  [6+
                   pivots[index], pivots[index]], linestyle="--", linewidth=1, marker=',')
      plt.annotate(str(pivots[index]), (mdates.date2num(dates[index]), pivots[index]), xytext=(-10, 7), 
              textcoords='offset points',fontsize=7, arrowprops=dict(arrowstyle='-|>'))
    
    # Customize
    plt.xlabel('Date') 
    plt.ylabel('Price')
    plt.title(stock+" - Daily") 
    plt.ylim(prices["Low"].min(), prices["High"].max()*1.05) 
    #plt.yscale("log")
    rcParams['figure.figsize'] = 20, 10
    plt.show()
    
    # Asks for new stock
    stock = input("Enter the stock symbol : ") 