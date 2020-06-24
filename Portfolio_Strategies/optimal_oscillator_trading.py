import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import mplfinance as mpf
import talib

# define time range 
start = dt.date.today() - dt.timedelta(days = 365)
end = dt.datetime.now()
stock='NIO'

df = yf.download(stock,start, end, interval='1d')

df["RSI"] = talib.RSI(df["Close"])
values = df["RSI"].tail(14)
value = values.mean()

position=0 # 1 means we have already entered poistion, 0 means not already entered
counter=0
percentChange=[]   # empty list to collect %changes 
for i in df.index:
    rsi=df['RSI']
    close=df['Adj Close'][i]
    
    if(rsi[i] <= 30):
        print('Up trend')
        if(position==0):
            buyP=close   #buy price
            position=1   # turn position
            print("Buy at the price: "+str(buyP))
        
    elif(rsi[i] >= 70):
        print('Down trend')
        if(position==1):   # have a position in down trend
            position=0     # selling position
            sellP=close    # sell price
            print("Sell at the price: "+str(sellP))
            perc=(sellP/buyP-1)*100
            percentChange.append(perc)
    if(counter==df["Adj Close"].count()-1 and position==1):
        position=0
        sellP=close
        print("Sell at the price: "+str(sellP))
        perc=(sellP/buyP-1)*100
        percentChange.append(perc)

    counter+=1
print('Percent Change on trades: '+ str(percentChange))
            
gains=0
numGains=0
losses=0
numLosses=0
totReturn=1
for i in percentChange:
    if(i>0):
        gains+=i
        numGains+=1
    else:
        losses+=i
        numLosses+=1
    totReturn = totReturn*((i/100)+1)
totReturn=round((totReturn-1)*100,2)
print("This statistics is from "+str(df.index[0])+" up to now with "+str(numGains+numLosses)+" trades:")
print("Total return over "+str(numGains+numLosses)+ " trades: "+ str(totReturn)+"%")

if (numGains>0):
    avgGain=gains/numGains
    maxReturn= str(max(percentChange))
else:
    avgGain=0
    maxReturn='unknown'

if(numLosses>0):
    avgLoss=losses/numLosses
    maxLoss=str(min(percentChange))
    ratioRR=str(-avgGain/avgLoss)  # risk-reward ratio
else:
    avgLoss=0
    maxLoss='unknown'
    ratioRR='inf'

df['PC'] = df['Close'].pct_change()
hold = round(df['PC'].sum() * 100, 2)
print ("Total return for a B&H strategy: " + str(hold)+'%')
print("Average Gain: "+ str(round(avgGain, 2)))
print("Average Loss: "+ str(round(avgLoss, 2)))
print("Max Return: "+ maxReturn)
print("Max Loss: "+ maxLoss)
print("Gain/loss ratio: "+ ratioRR)

if(numGains>0 or numLosses>0):
    batAvg=numGains/(numGains+numLosses)
else:
    batAvg=0
print("Batting Avg: "+ str(batAvg))

from matplotlib import dates as mdates
dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
dfc = dfc.reset_index()
dfc['Date'] = dfc['Date'].map(mdates.date2num)

from mplfinance.original_flavor import candlestick_ohlc

fig = plt.figure(figsize=(14,7))
ax1 = plt.subplot(2, 1, 1)
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title(stock +' Closing Price')
ax1.set_ylabel('Price')

ax2 = plt.subplot(2, 1, 2)
ax2.plot(df['RSI'], label='Relative Strength Index')
ax2.text(s='Overbought', x=df.RSI.index[10], y=70, fontsize=12)
ax2.text(s='Oversold', x=df.RSI.index[10], y=30, fontsize=12)
ax2.axhline(y=70, color='red')
ax2.axhline(y=30, color='red')
ax2.grid()
ax2.set_ylabel('RSI')
ax2.set_xlabel('Date')
ax2.legend(loc='best')
plt.show()