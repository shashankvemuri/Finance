import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import matplotlib.dates as mdates

ticker = input("Enter a ticker: ")
ticker = str(ticker)

num_of_years = 6
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 

stock = DataReader(ticker, 'yahoo', start_date, end_date)

#Creating Simple Moving Average with 30-day Window
SMA30 = pd.DataFrame()
SMA30['Close Price'] = stock['Close'].rolling(window=30).mean()

#Creating Simple Moving Average with 100-day Window
SMA100 = pd.DataFrame()
SMA100['Close Price'] = stock['Close'].rolling(window=100).mean()

#Creating a new dataframe to store all data
data = pd.DataFrame()
data['stock'] = stock['Close']
data['SMA 30'] = SMA30['Close Price']
data['SMA 100'] = SMA100['Close Price']

def buy_sell(data):
  sigPriceBuy=[]
  sigPriceSell=[]
  flag=-1


  for i in range(len(data)):
    if data['SMA 30'][i]>data['SMA 100'][i]:
      if flag != 1:
        sigPriceBuy.append(data['stock'][i])
        sigPriceSell.append(np.nan)
        flag=1
      else:
        sigPriceBuy.append(np.nan)
        sigPriceSell.append(np.nan)
    elif data['SMA 30'][i]<data['SMA 100'][i]:
      if flag != 0 :
        sigPriceBuy.append(np.nan)
        sigPriceSell.append(data['stock'][i])
        flag = 0
      else:
        sigPriceBuy.append(np.nan)
        sigPriceSell.append(np.nan)
    else:
      sigPriceBuy.append(np.nan)
      sigPriceSell.append(np.nan)


  return(sigPriceBuy,sigPriceSell)

buy_sell = buy_sell(data)
data['Buy_Signal_Price'] = buy_sell[0]
data['Sell_Signal_Price'] = buy_sell[1]

#Visualize the Data
plt.figure(figsize=(15,10))
plt.plot(stock['Close'],label = f'{ticker.upper()} Close Price',alpha=0.35)
plt.plot(SMA30['Close Price'],label = 'SMA 30' ,alpha=0.35)
plt.plot(SMA100['Close Price'],label = 'SMA 100' ,alpha=0.35)
plt.scatter(data.index,data['Buy_Signal_Price'],label='Buy',marker='^',color='green')
plt.scatter(data.index,data['Sell_Signal_Price'],label='Sell',marker='v',color='red')
plt.title(f'{ticker.upper()} Close Price History Buy and Sell Signals')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend(loc='upper left')
plt.show()