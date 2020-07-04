from financeAPI import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from urllib.request import urlopen

with open('Secret_Key.txt') as f:
    key = f.read()

f = FinanceAPI()

f.build_dict('AAPL')
f.registerKey_(key)

apple_dict=f.build_dict('AAPL')
for k,v in apple_dict.items():
    print("{}: {}".format(k,v))

df=f.build_dataframe(['TWTR','FB','MSFT','NVDA','AAPL','CRM'])
f.available_data('profile')
f.available_data('metrics')
f.available_data('ratios')

f.bar_chart('Book Value per Share',color='orange',edgecolor='k')
f.bar_chart('debtEquityRatio')

f.scatter('quickRatio','Book Value per Share',color='blue')
f.scatter(varX='debtEquityRatio',
          varY='Enterprise Value over EBITDA',
         sizeZ='price',
         color='red',alpha=0.6)

# Only companies with market cap > 200 billion USD
df = f.df
df_large_cap = df[df['Market Cap']>200e9]
df_large_cap[['companyName','Market Cap']]

# A fresh class declration
f2 = FinanceAPI()
# Assigning the custom DataFrame to the `df` attribute of this new class object
# Note we did not need to request data from the API again.
f2.df = df_large_cap

f2.bar_chart('Enterprise Value over EBITDA',color='red',edgecolor='k')