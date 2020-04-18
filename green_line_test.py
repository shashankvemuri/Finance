import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr

yf.pdr_override() # <== that's all it takes :-)
start =dt.datetime(1980,12,1)
now = dt.datetime.now()
stock=""

stock = input("Enter the stock symbol : ") 
while stock != "quit":
  df = pdr.get_data_yahoo(stock, start, now)

  df.drop(df[df["Volume"]<1000].index, inplace=True)

  dfmonth=df.groupby(pd.Grouper(freq="M"))["High"].max()

  glDate=0
  lastGLV=0
  currentDate=""
  curentGLV=0
  for index, value in dfmonth.items():
    if value > curentGLV:
      curentGLV=value
      currentDate=index
      counter=0
    if value < curentGLV:
      counter=counter+1

      if counter==3 and ((index.month != now.month) or (index.year != now.year)):
          if curentGLV != lastGLV:
            print(curentGLV)
          glDate=currentDate
          lastGLV=curentGLV
          counter=0

  if lastGLV==0:
    message=stock+" has not formed a green line yet"
  else:
    message=("Last Green Line: "+str(lastGLV)+" on "+str(glDate))

  print(message)
  stock = input("Enter the stock symbol : ") 


