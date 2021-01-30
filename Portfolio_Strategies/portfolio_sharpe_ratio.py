'''
399    REGN      5.016115
459     UNH      5.150879
107      CI      5.276706
78      BMY      5.651378
7       AMD      5.781002
419    SWKS      5.869410
48     AAPL      6.083879
20      AGN      6.312075
242     HUM      6.329243
39     AMGN      6.460227
'''

import pandas as pd
from pandas_datareader.data import DataReader

start_date = '2019-9-30'
end_date = '2019-12-31'
stock = 'REGN' 
stock1 = 'UNH'
stock2 = 'CI'
stock3 = 'BMY'
stock4 = 'AMD'
stock5 = 'SWKS'
stock6 = 'AAPL'
stock7 = 'AGN'
stock8 = 'HUM'
stock9 = 'AMGN'


invest1 = DataReader(stock, 'yahoo', start_date, end_date) 
x = 20000 #dollars, 45 stocks
invest2 = DataReader(stock1, 'yahoo', start_date, end_date) 
x1 = 20000 #dollars, 65 stocks
invest3 = DataReader(stock2, 'yahoo', start_date, end_date) 
x2 = 20000 #dollars, 20 stocks
invest4 = DataReader(stock3, 'yahoo', start_date, end_date)  
x3 = 20000 #dollars, 25 stocks
invest5 = DataReader(stock4, 'yahoo', start_date, end_date)  
x4 = 20000 #dollars, 46 stocks
invest6 = DataReader(stock5, 'yahoo', start_date, end_date) 
x5 = 20000 #dollars, 45 stocks
invest7 = DataReader(stock6, 'yahoo', start_date, end_date) 
x6 = 20000 #dollars, 65 stocks
invest8 = DataReader(stock7, 'yahoo', start_date, end_date) 
x7 = 20000 #dollars, 20 stocks
invest9 = DataReader(stock8, 'yahoo', start_date, end_date)  
x8 = 20000 #dollars, 46 stocks
invest10 = DataReader(stock9, 'yahoo', start_date, end_date)  
x9 = 20000 #dollars, 25 stocks


y = (x + x1 + x2 + x3 + x4)

for stock_df in (invest1, invest2, invest3, invest4, invest5, invest6, invest7, invest8, invest9, invest10):
    stock_df['Norm return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']

for stock_df, allocation in zip((invest1, invest2, invest3, invest4, invest5, invest6, invest7, invest8, invest9, invest10),[float(x/y),float(x1/y),float(x2/y),float(x3/y),float(x4/y), float(x5/y), float(x6/y), float(x7/y), float(x8/y), float(x9/y)]):
    stock_df['Allocation'] = stock_df['Norm return'] * allocation

for stock_df in (invest1, invest2, invest3, invest4, invest5, invest6, invest7, invest8, invest9, invest10):
    stock_df['Position'] = stock_df['Allocation']*100000

all_pos = [invest1['Position'], invest2['Position'], invest3['Position'], invest4['Position'], invest5['Position'], invest6['Position'], invest7['Position'], invest8['Position'], invest9['Position'], invest10['Position']]
portf_val = pd.concat(all_pos, axis=1)
portf_val.columns = ['{} Pos'.format(stock), '{} Pos'.format(stock1), '{} Pos'.format(stock2), '{} Pos'.format(stock3), '{} Pos'.format(stock4), '{} Pos'.format(stock5), '{} Pos'.format(stock6), '{} Pos'.format(stock7), '{} Pos'.format(stock8), '{} Pos'.format(stock9)]
portf_val['Total Pos'] = portf_val.sum(axis=1)
print(portf_val)


import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
portf_val['Total Pos'].plot(figsize=(10,8))

portf_val.drop('Total Pos', axis=1).plot(figsize=(10,8))

cumulative_return = 100 * ( portf_val [ 'Total Pos' ] [-1 ] / portf_val [ 'Total Pos' ] [ 0 ] -1)
print('Your initial portfolio value is {:.2f} '.format(y))
print('Your cumulative return was {:.2f}% '.format(cumulative_return))
print('Your investment is now valued at {:.2f} dollars '.format(cumulative_return/100 *y + y))

portf_val.tail(1)

portf_val['Daily Return'] = portf_val['Total Pos'].pct_change(1)

Sharpe_Ratio = portf_val['Daily Return'].mean() / portf_val['Daily Return'].std()

A_Sharpe_Ratio = (252**0.5) * Sharpe_Ratio
print (A_Sharpe_Ratio)