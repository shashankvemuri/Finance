# Import dependencies
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
from pylab import rcParams
yf.pdr_override()

# Set the number of years to fetch the data for and the start date
num_of_years = 40
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))

# Set the current date
now = dt.date(2020, 10, 3)

# Ask for stock ticker and run until user enters 'quit'
stock = input("Enter the stock symbol: ")

while stock.lower() != "quit":

    # Create Plots
    fig, ax1 = plt.subplots()

    # Fetch stock price data and save as a data frame
    df = pdr.get_data_yahoo(stock, start, now)
    print(df.tail(1))

    # Calculate the Simple Moving Average and create a new column in the data frame
    sma = 50
    df['SMA'+str(sma)] = df.iloc[:,4].rolling(window=sma).mean()
    
    # Calculate percentage change and create a new column in the data frame
    df['PC'] = ((df["Adj Close"]/df['SMA'+str(sma)])-1)*100

    # Calculate mean, standard deviation, current, and yesterday's percentage change
    mean = round(df["PC"].mean(), 2)
    stdev = round(df["PC"].std(), 2)
    current = round(df["PC"][-1], 2)
    yday = round(df["PC"][-2], 2)

    # Print calculated values
    print("Mean: "+str(mean))
    print("Standard Dev: "+str(stdev))
    print("Current: " + str(current))
    print("Yesterday: " + str(yday))

    # Set the bin size
    bins = np.arange(-100, 100, 1)

    # Set the size of the plot
    rcParams['figure.figsize'] = 15, 10

    # Set the x-axis limits
    plt.xlim([df["PC"].min()-5, df["PC"].max()+5])

    # Create histogram
    plt.hist(df["PC"], bins=bins, alpha=0.5)

    # Set the plot title, x-axis label, and y-axis label
    plt.title(stock+"-- % From "+str(sma)+" SMA Histogram since "+str(start.year))
    plt.xlabel('Percent from '+str(sma)+' SMA (bin size = 1)')
    plt.ylabel('Count')

    # Add vertical lines to the plot for mean and standard deviation
    plt.axvline(x=mean, ymin=0, ymax=1, color='k', linestyle='--')
    plt.axvline(x=stdev+mean, ymin=0, ymax=1, color='gray', alpha=1, linestyle='--')
    plt.axvline(x=2*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.75, linestyle='--')
    plt.axvline(x=3*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.5, linestyle='--')
    plt.axvline(x=-stdev+mean, ymin=0, ymax=1, color='gray', alpha=1, linestyle='--')
    plt.axvline(x=-2*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.75, linestyle='--')
    plt.axvline(x=-3*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.5, linestyle='--')
    plt.axvline(x=current, ymin=0, ymax=1, color='r', label = 'today')
    plt.axvline(x=yday, ymin=0, ymax=1, color='blue', label = 'yesterday')
    
    # Add more x axis labels
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(14)) 
    
    # Create Plots
    fig2, ax2 = plt.subplots() 
    
    # Percent from SMA Chart
    df=df[-150:]
    df['PC'].plot(label='close',color='k')
    plt.title(stock+"-- % From "+str(sma)+" SMA Over last 100 days")
    plt.xlabel('Date') 
    plt.ylabel('Percent from '+str(sma)+' SMA')

    # Add more x axis labels
    limit = 10
    ax2.xaxis.set_major_locator(mticker.MaxNLocator(8)) 
    plt.axhline(y=limit, xmin=0, xmax=1, color='r')
    rcParams['figure.figsize'] = 15, 10
    plt.show()
    
    stock = input("Enter the stock symbol: ") 