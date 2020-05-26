import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)
start =dt.datetime(1980,12,1)
now = dt.datetime.now()
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pandas import ExcelWriter
from pandas import ExcelFile
from openpyxl import Workbook
import os

root = Tk()
ftypes = [(".xlsm","*.xlsx",".xls")]
ttl  = "Title"
dir1 = 'C:\\'
#Input a file with symbols in first column
root.fileName = askopenfilename(filetypes = ftypes, initialdir = dir1, title = ttl)
print (root.fileName)

GLlistDATA = pd.DataFrame(columns=['Stock', "Last Greenline", "Date"])

a = pd.read_excel(root.fileName, index_col=0, index_row=0, header=None)
for index, value in a.iterrows():
  stock=index
  df = pdr.get_data_yahoo(stock, start, now)
  df.drop(df[df["Volume"]<1000].index, inplace=True)
  dfmonth=df.groupby(pd.Grouper(freq='M'))['High'].max()
  DOH=""
  GLV=0
  DOHc=""
  GLVc=0
  counter=0
  for index, value in dfmonth.items():
    if value> GLVc:
      GLVc=value
      DOHc=index
      counter=0
    if value < GLVc:
      counter=counter+1
      if counter==3 and ((index.month != now.month) or (index.year != now.year) ):
        GLV=GLVc
        counter=0
        DOH=DOHc
        print(str(DOH))
  GLlistDATA = GLlistDATA.append({'Stock': stock,'Greenline': GLV, 'Date': DOH}, ignore_index=True)
 
print(GLlistDATA)
newFile=os.path.dirname(root.fileName)+"/output.xlsx"
print(newFile)

writer = ExcelWriter(newFile)
GLlistDATA.to_excel(writer,'Sheet1')
writer.save() 



