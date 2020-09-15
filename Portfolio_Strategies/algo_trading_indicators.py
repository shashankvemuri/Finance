import yfinance as yf
import datetime as dt
import warnings
import talib 
import pandas as pd
import time
from yahoo_fin import stock_info as si
from scipy.stats import zscore
import numpy as np


warnings.filterwarnings("ignore")
yf.pdr_override()
pd.set_option('display.max_columns', None)

ticker = input('Enter a ticker: ')
num_of_years = float(input('Enter the number of years: '))

start = dt.date.today() - dt.timedelta(days = int(365.25 * num_of_years))
end = dt.date.today()
tickers = [f'{ticker}']

spy = yf.download('SPY',start,end, interval='1d')
spy['RSI'] = talib.RSI(spy['Adj Close'], timeperiod=14)

for symbol in tickers:
    # Read df 
    df = yf.download(symbol,start,end, interval='1d')
    
    # Bollinger Bands
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['Adj Close'], timeperiod=14)
    df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Adj Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI'] = talib.RSI(df['Adj Close'], timeperiod=14)
    df['Momentum'] = talib.MOM(df['Adj Close'], timeperiod=14)
    df['Z-Score'] = zscore(df['Adj Close'])
    df['BBANDS_Position'] = None
    df['MACD_Position'] = None
    df['rsiPos'] = None
    df['spy_rsiPos'] = None
    df['zPos'] = None
    df['momentumPos'] = None

    for row in range(len(df)):
        
        if (df['Adj Close'].iloc[row] > df['upper_band'].iloc[row]) and (df['Adj Close'].iloc[row-1] < df['upper_band'].iloc[row-1]):
            df['BBANDS_Position'].iloc[row] = -1
        elif (df['Adj Close'].iloc[row] < df['lower_band'].iloc[row]) and (df['Adj Close'].iloc[row-1] > df['lower_band'].iloc[row-1]):
            df['BBANDS_Position'].iloc[row] = 1
        else:
            df['BBANDS_Position'].iloc[row] = 0
            
        if (df['macd'].iloc[row] > df['macdsignal'].iloc[row]):
            df['MACD_Position'].iloc[row] = 1
        elif (df['macd'].iloc[row] < df['macdsignal'].iloc[row]):
            df['MACD_Position'].iloc[row] = -1
        else:
            df['MACD_Position'].iloc[row] = 0
    
        if (df['RSI'].iloc[row] < 30):
            df['rsiPos'].iloc[row] = 1
        elif (df['RSI'].iloc[row] > 70):
            df['rsiPos'].iloc[row] = -1
        else:
            df['rsiPos'].iloc[row] = 0
        
        if (spy['RSI'].iloc[row] < 30):
            df['spy_rsiPos'].iloc[row] = 1
        elif (spy['RSI'].iloc[row] > 70):
            df['spy_rsiPos'].iloc[row] = -1
        else:
            df['spy_rsiPos'].iloc[row] = 0
            
        if (df['Z-Score'].iloc[row] >= -1.5):
            df['zPos'].iloc[row] = 1
        else:
            df['zPos'].iloc[row] = 0
            
        if (df['Momentum'].iloc[row] > -0.2):
            df['momentumPos'].iloc[row] = 1
        elif (df['Momentum'].iloc[row] < 0.1):
            df['momentumPos'].iloc[row] = -1
        else:
            df['momentumPos'].iloc[row] = 0
    position=0 # 1 means we have already entered poistion, 0 means not already entered
    counter=0
    percentChange=[]   # empty list to collect %changes 
    
    df = df.iloc[33:]
    spy = spy.iloc[33:]
    for i in df.index:
        
        bbandsPos=df['BBANDS_Position']
        macdPos=df['MACD_Position']
        rsiPos = df['rsiPos']
        rsi_spy = df['spy_rsiPos']
        momentumPos = df['momentumPos']
        zPos = df['zPos']
        close=df['Adj Close'][i]
        
        if(((bbandsPos[i] == 1) and (rsiPos[i]==1) and (rsi_spy[i] != 1))):
    
            if(position==0):
                buyP=close   #buy price
                position=1   # turn position

        elif(((momentumPos[i] == 1) and (zPos[i]==1) and (macdPos[i] == 1))):
            if(position==0):
                buyP=close   #buy price
                position=1   # turn position
            
        elif(((bbandsPos[i] == -1) and (rsiPos[i]==-1) and (rsi_spy[i]!= -1))):
    
            if(position==1):   # have a poistion in down trend
                position=0     # selling position
                sellP=close    # sell price
    
                perc=(sellP/buyP-1)*100
                percentChange.append(perc)
        
        elif(((momentumPos[i]==-1) and (macdPos[i] == -1))):
    
            if(position==1):   # have a poistion in down trend
                position=0     # selling position
                sellP=close    # sell price
    
                perc=(sellP/buyP-1)*100
                percentChange.append(perc)
        if(counter==df["Adj Close"].count()-1 and position==1):
            position=0
            sellP=close
    
            perc=(sellP/buyP-1)*100
            percentChange.append(perc)
    
        counter+=1
    
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
    print("These statistics are from "+str(start)+" up till now with "+str(numGains+numLosses)+" trades:")
    print("Total return over "+str(numGains+numLosses)+ " trades: "+ str(totReturn)+"%")
    
    if (numGains>0):
        avgGain=gains/numGains
        maxReturn= str(max(percentChange))
    else:
        avgGain=0
        maxReturn=np.nan
    
    if(numLosses>0):
        avgLoss=losses/numLosses
        maxLoss=str(min(percentChange))
        ratioRR=str(-avgGain/avgLoss)  # risk-reward ratio
    else:
        avgLoss=0
        maxLoss=np.nan
        ratioRR='inf'
    
    df['PC'] = df['Close'].pct_change()
    hold = round(df['PC'].sum() * 100, 2)
    print ("Total return for a B&H strategy: " + str(hold)+'%')
    print("Average Gain: "+ str(round(avgGain, 2)))
    print("Average Loss: "+ str(round(avgLoss, 2)))
    print("Max Return: "+ str(maxReturn))
    print("Max Loss: "+ str(maxLoss))
    print("Gain/loss ratio: "+ str(ratioRR))
    
    if(numGains>0 or numLosses>0):
        batAvg=numGains/(numGains+numLosses)
    else:
        batAvg=0
    print("Batting Avg: "+ str(batAvg))