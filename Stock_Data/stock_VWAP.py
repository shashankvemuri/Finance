import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import datetime as dt

stock = 'AAPL'

def get_symbol(symbol):
    num_of_years = 1
    start = dt.date.today() - dt.timedelta(days=365*num_of_years)
    end = dt.date.today()
    df = pdr.get_data_yahoo(symbol, start, end)
    return df

def VWAP():
    df = get_symbol(stock)
    df['Typical_Price'] = (df['High']+df['Low']+df['Adj Close'])/3
    df['TP_Volume'] = df['Typical_Price'] * df['Volume']
    Cumulative_TP_V = df['TP_Volume'].sum() 
    Cumulative_V = df['Volume'].sum()
    vwap = Cumulative_TP_V/Cumulative_V
    return vwap

print(VWAP())

def Update_VWAP():
    df = get_symbol(stock)
    df['OpenxVolume'] = df['Open']*df['Volume']
    df['HighxVolume'] = df['High']*df['Volume']
    df['LowxVolume'] = df['Low']*df['Volume']
    df['ClosexVolume'] = df['Adj Close']*df['Volume']
    Sum_Volume = df['Volume'].sum()
    Sum_x_OV = df['OpenxVolume'].sum()/ Sum_Volume
    Sum_x_HV = df['HighxVolume'].sum()/ Sum_Volume
    Sum_x_LV = df['LowxVolume'].sum()/ Sum_Volume
    Sum_x_CV = df['ClosexVolume'].sum()/ Sum_Volume
    Average_Volume_Each = (Sum_x_OV + Sum_x_HV + Sum_x_LV + Sum_x_OV)/4
    new_vwap = ((df['Adj Close'][-1] - Average_Volume_Each)+(df['Adj Close'][-1] + Average_Volume_Each))/2
    return new_vwap

print(Update_VWAP())

def VWAP_Column():
    df = get_symbol('AAPL')
    df['OpenxVolume'] = df['Open']*df['Volume']
    df['HighxVolume'] = df['High']*df['Volume']
    df['LowxVolume'] = df['Low']*df['Volume']
    df['ClosexVolume'] = df['Adj Close']*df['Volume']
    vwap_column = (df[['OpenxVolume','HighxVolume','LowxVolume','ClosexVolume']].mean(axis=1))/df['Volume']
    return vwap_column

print(Update_VWAP())