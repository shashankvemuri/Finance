import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
from pylab import rcParams

yf.pdr_override() 

num_of_years = 40
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
now = dt.datetime.now() 

#Asks for stock ticker
stock = input("Enter the stock symbol : ") 

#Runs this loop until user enters 'quit' (can do many stocks in a row)
while stock != "quit": 
    
    #Create Plots
    fig, ax1 = plt.subplots() 
    
    #Fetches stock price data, saves as data frame
    df = pdr.get_data_yahoo(stock, start, now)
    
    #Asks for stock ticker
    sma = int(input("Enter the sma : ")) 
    limit= int(input("Enter Warning Limit : "))
    
    #calculates sma and creates a column in the dataframe
    df['SMA'+str(sma)] = df.iloc[:,4].rolling(window=sma).mean() 
    df['PC'] = ((df["Adj Close"]/df['SMA'+str(sma)])-1)*100
    
    mean =df["PC"].mean()
    stdev=df["PC"].std()
    current=df["PC"][-1]
    yday=df["PC"][-2]
    
    print(str(current))
    
    print("Mean: "+str(mean))
    print("Standard Dev: "+str(stdev))
    
    # fixed bin size
    bins = np.arange(-100, 100, 1) 
    rcParams['figure.figsize'] = 15, 10
    plt.xlim([df["PC"].min()-5, df["PC"].max()+5])
    
    plt.hist(df["PC"], bins=bins, alpha=0.5)
    plt.title(stock+"-- % From "+str(sma)+" SMA Histogram since "+str(start.year))
    plt.xlabel('Percent from '+str(sma)+' SMA (bin size = 1)')
    plt.ylabel('Count')
    
    plt.axvline( x=mean, ymin=0, ymax=1, color='k', linestyle='--')
    plt.axvline( x=stdev+mean, ymin=0, ymax=1, color='gray', alpha=1, linestyle='--')
    plt.axvline( x=2*stdev+mean, ymin=0, ymax=1, color='gray',alpha=.75, linestyle='--')
    plt.axvline( x=3*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.5, linestyle='--')
    plt.axvline( x=-stdev+mean, ymin=0, ymax=1, color='gray', alpha=1, linestyle='--')
    plt.axvline( x=-2*stdev+mean, ymin=0, ymax=1, color='gray',alpha=.75, linestyle='--')
    plt.axvline( x=-3*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.5, linestyle='--')
    
    plt.axvline( x=current, ymin=0, ymax=1, color='r', label = 'today')
    plt.axvline( x=yday, ymin=0, ymax=1, color='blue', label = 'yesterday')
    
    #add more x axis labels
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(14)) 
    
    #Create Plots
    fig2, ax2 = plt.subplots() 
    
    df=df[-150:]
    
    df['PC'].plot(label='close',color='k')
    plt.title(stock+"-- % From "+str(sma)+" SMA Over last 100 days")
    plt.xlabel('Date') 
    plt.ylabel('Percent from '+str(sma)+' EMA')

    #add more x axis labels
    ax2.xaxis.set_major_locator(mticker.MaxNLocator(8)) 
    plt.axhline( y=limit, xmin=0, xmax=1, color='r')
    rcParams['figure.figsize'] = 15, 10
    plt.show()
    
    stock = input("Enter the stock symbol : ") 
