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

#Creating Simple Moving Average with 50-day Window
SMA50 = pd.DataFrame()
SMA50['Close Price'] = stock['Close'].rolling(window=50).mean()

#Creating Simple Moving Average with 200-day Window
SMA200 = pd.DataFrame()
SMA200['Close Price'] = stock['Close'].rolling(window=200).mean()

#Creating a new dataframe to store all data
data = pd.DataFrame()
data['stock'] = stock['Close']
data['SMA 50'] = SMA50['Close Price']
data['SMA 200'] = SMA200['Close Price']

def buy_sell(data):
  sigPriceBuy=[]
  sigPriceSell=[]
  flag=-1


  for i in range(len(data)):
    if data['SMA 50'][i]>data['SMA 200'][i]:
      if flag != 1:
        sigPriceBuy.append(data['stock'][i])
        sigPriceSell.append(np.nan)
        flag=1
      else:
        sigPriceBuy.append(np.nan)
        sigPriceSell.append(np.nan)
    elif data['SMA 50'][i]<data['SMA 200'][i]:
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
plt.plot(SMA50['Close Price'],label = 'SMA 50' ,alpha=0.35)
plt.plot(SMA200['Close Price'],label = 'SMA 200' ,alpha=0.35)
plt.scatter(data.index,data['Buy_Signal_Price'],label='Buy',marker='^',color='green')
plt.scatter(data.index,data['Sell_Signal_Price'],label='Sell',marker='v',color='red')
plt.title(f'{ticker.upper()} Close Price History Buy and Sell Signals')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend(loc='upper left')
plt.show()