import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt 

# input
symbol = 'SPY'
start = dt.date.today() - dt.timedelta(days = 365*4)
end = dt.date.today()

# Read data 
df = yf.download(symbol,start,end)
df['Adj Close'][1:]

import talib as ta


# ## On Balance Volume
OBV = ta.OBV(df['Adj Close'], df['Volume'])

import quandl as q

Advances = q.get('URC/NYSE_ADV', start_date = "2017-07-27")['Numbers of Stocks']
Declines = q.get('URC/NYSE_DEC', start_date = "2017-07-27")['Numbers of Stocks']  

adv_vol = q.get("URC/NYSE_ADV_VOL", start_date = "2017-07-27")['Numbers of Stocks']
dec_vol = q.get("URC/NYSE_DEC_VOL", start_date = "2017-07-27")['Numbers of Stocks']

data = pd.DataFrame()
data['Advances'] = Advances
data['Declines'] = Declines
data['adv_vol'] = adv_vol
data['dec_vol'] = dec_vol

data['Net_Advances'] = data['Advances'] - data['Declines'] 
data['Ratio_Adjusted'] = (data['Net_Advances']/(data['Advances'] + data['Declines'])) * 1000
data['19_EMA'] = ta.EMA(data['Ratio_Adjusted'], timeperiod=19)
data['39_EMA'] = ta.EMA(data['Ratio_Adjusted'], timeperiod=39)
data['RANA'] = (data['Advances'] - data['Declines']) / (data['Advances'] + data['Declines']) * 1000

# Finding the TRIN Value
data['ad_ratio'] = data['Advances'].divide(data['Declines'] ) # AD Ratio
data['ad_vol'] = data['adv_vol'].divide(data['dec_vol']) # AD Volume Ratio
data['TRIN'] = data['ad_ratio'].divide(data['adv_vol']) # TRIN Value

# ## Force Index

def ForceIndex(data,n):
    ForceIndex=pd.Series(df['Adj Close'].diff(n)* df['Volume'],name='ForceIndex')
    data = data.join(ForceIndex)
    return data

n=10
ForceIndex = ForceIndex(data,n)
ForceIndex = ForceIndex['ForceIndex']

fig=plt.figure(figsize=(7,5))
ax=fig.add_subplot(2,1,1)
ax.set_xticklabels([])
plt.plot(df['Adj Close'],lw=1)
plt.title('Market Price Chart')
plt.ylabel('Close Price')
plt.grid(True)
bx=fig.add_subplot(2,1,2)
plt.plot(ForceIndex,'k',lw=0.75,linestyle='-',label='Force Index')
plt.legend(loc=2,prop={'size':9.5})
plt.ylabel('Force Index')
plt.grid(True)
plt.setp(plt.gca().get_xticklabels(),rotation=30)
plt.show()


# ## Chaikin Oscillator
def Chaikin(data):
    money_flow_volume = (2 * df['Adj Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['Volume']  
    ad = money_flow_volume.cumsum()
    Chaikin = pd.Series(ad.ewm(com=(3-1)/2).mean() - ad.ewm(com=(10-1)/2).mean(), name='Chaikin')
    data = data.join(Chaikin)  
    return data


Chaikin(df)

Up = q.get('URC/NYSE_ADV', start_date = "2017-07-27")['Numbers of Stocks']
Down = q.get('URC/NYSE_DEC', start_date = "2017-07-27")['Numbers of Stocks']
Volume_Spread = Up - Down

Up = q.get('URC/NYSE_ADV', start_date = "2017-07-27")['Numbers of Stocks']
Down = q.get('URC/NYSE_DEC', start_date = "2017-07-27")['Numbers of Stocks']
Volume_Ratio = Up/Down


# ## Cumulative Volume Index
# CVI = Yesterday's CVI + (Advancing Volume - Declining Volume)
data['CVI'] = data['Net_Advances'][1:] + (data['Advances'] - data['Declines']) 