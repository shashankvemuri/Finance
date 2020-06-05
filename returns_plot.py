import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import pandas as pd
from pandas_datareader import DataReader

start_date = dt.datetime.now() - dt.timedelta(days=int(365.25*10))
end_date = dt.date.today()

ticker=input('Enter a ticker: ')

def compute_daily_return(df):
    daily_ret=df.copy()
    daily_ret[1:]=(df[1:]/df[:-1].values)-1
    daily_ret.ix[0]=0
    return daily_ret
def plot_data(df, title="Stock prices"):
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def dailyreturnplot():
    df = DataReader(ticker, 'yahoo', start_date, end_date)['Close']
    df.fillna(method="ffill",inplace=True)
    df.fillna(method="bfill",inplace=True)
    dailyreturn=compute_daily_return(df)
    plot_data(dailyreturn,title="Daily returns")
    
dailyreturnplot()
