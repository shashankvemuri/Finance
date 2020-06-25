import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import DataReader

start_date = dt.datetime.now() - dt.timedelta(days=int(365.25*10))
end_date = dt.date.today()

#type(ticker)

def get_rolling_mean(values, window):
    return values.rolling(window).mean()

def get_rolling_std(values, window):
    return values.rolling(window).std()

def get_rolling_median(values, window):
    return values.rolling(window).median()

def custom_stats(var1,var2,var3,ticker):
    
    df = DataReader(ticker, 'yahoo', start_date, end_date)['Close']
    df.fillna(method="ffill",inplace=True)
    df.fillna(method="bfill",inplace=True)
    ax = df.plot(title="Custom Stats", label=ticker)
    
    def plot_mean():
        RollingMean = get_rolling_mean(df, window=20)
        RollingMean.plot(label='Rolling Mean', ax=ax)

    def plot_std():
        RollingStd = get_rolling_std(df, window=20)
        RollingStd.plot(label='Rolling Standard', ax=ax)

    def plot_median():
        RollingMedian = get_rolling_median(df,window=20)
        RollingMedian.plot(label='Rolling Median',ax=ax)
    if(var1==1):
        plot_mean()
        if(var2==1):
            plot_std()
            if(var3==1):
                plot_median()
        else:
            if(var3==1):
                plot_median()
    else:
        if(var2==1):
            plot_std()
            if(var3==1):
                plot_median()
        else:
            if(var3==1):
                plot_median()
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()

custom_stats(1, 1, 1, input('Enter a ticker: '))
