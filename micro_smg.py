import pandas as pd
from pandas_datareader.data import DataReader

walmart = DataReader('WMT', 'yahoo', '2019-12-11', '2019-12-12') 
x = 12574.8 #dollars, 105 stocks
merck = DataReader('MRK', 'yahoo', '2019-12-11', '2019-12-12')  
x1 = 10299.40 #dollars, 115 stocks
nike = DataReader('NKE', 'yahoo', '2019-12-11', '2019-12-12') 
x2 = 9768 #dollars, 100 stocks
starbucks = DataReader('SBUX', 'yahoo', '2019-12-11', '2019-12-12') 
x3 = 9438.47 #dollars, 107 stocks

y = (x + x1 + x2 + x3)

for stock_df in (walmart, merck, nike, starbucks):
    stock_df['Norm return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']

for stock_df, allocation in zip((walmart, merck, nike, starbucks),[float(x/y),float(x1/y),float(x2/y),float(x3/y)]):
    stock_df['Allocation'] = stock_df['Norm return'] * allocation

for stock_df in (walmart, merck, nike, starbucks):
    stock_df['Position'] = stock_df['Allocation']*100000

all_pos = [walmart['Position'], merck['Position'], nike['Position'], starbucks['Position']]
portf_val = pd.concat(all_pos, axis=1)
portf_val.columns = ['WMT Pos', 'MRCK Pos', 'NKE Pos', 'SBUX Pos']
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