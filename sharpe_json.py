#class sharpe_ratio:
    
import pandas as pd
from pandas_datareader.data import DataReader
from flask import Flask, jsonify, request

app = Flask(__name__)

walmart = DataReader('WMT', 'yahoo', '2019-06-10', '2019-09-10')
macy = DataReader('M', 'yahoo', '2019-06-10', '2019-09-10')
merck = DataReader('MRK', 'yahoo', '2019-06-10', '2019-09-10')
target = DataReader('TGT', 'yahoo', '2019-06-10', '2019-09-10')
NI = DataReader('NI', 'yahoo', '2019-06-10', '2019-09-10')
FSUVX = DataReader('FSUVX', 'yahoo', '2019-06-10', '2019-09-10')
nike = DataReader('NKE', 'yahoo', '2019-06-10', '2019-09-10')
axp = DataReader('AXP', 'yahoo', '2019-06-10', '2019-09-10')
pg = DataReader('PG', 'yahoo', '2019-06-10', '2019-09-10')
SOXX = DataReader('SOXX', 'yahoo', '2019-06-10', '2019-09-10')
starbucks = DataReader('SBUX', 'yahoo', '2019-06-10', '2019-09-10')
coka = DataReader('KO', 'yahoo', '2019-06-10', '2019-09-10')
mdlz = DataReader('MDLZ', 'yahoo', '2019-06-10', '2019-09-10')

for stock_df in (walmart, merck, FSUVX, nike, axp, pg, SOXX, starbucks, coka, mdlz):
    stock_df['Norm return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']

for stock_df, allocation in zip((walmart, merck, FSUVX, nike, axp, pg, SOXX, starbucks, coka, mdlz),[.1,.1,.1,.1,.1,.1,.1,.1,.1,.1]):
    stock_df['Allocation'] = stock_df['Norm return'] * allocation

for stock_df in (walmart, merck, FSUVX, nike, axp, pg, SOXX, starbucks, coka, mdlz):
    stock_df['Position'] = stock_df['Allocation']*100000

all_pos = [walmart['Position'], merck['Position'], FSUVX['Position'], nike['Position'], axp['Position'], pg['Position'], SOXX['Position'], starbucks['Position'], coka['Position'], mdlz['Position']]
portf_val = pd.concat(all_pos, axis=1)
portf_val.columns = ['WMT Pos','MRCK Pos','FSUVX Pos', 'NKE Pos', 'AXP Pos', 'PG Pos', 'SOXX Pos', 'SBUX Pos', 'KO Pos', 'MDLZ Pos']
portf_val['Total Pos'] = portf_val.sum(axis=1)
print(portf_val.head())

import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
portf_val['Total Pos'].plot(figsize=(10,8))

portf_val.drop('Total Pos', axis=1).plot(figsize=(10,8))

cumulative_return = 100 * ( portf_val [ 'Total Pos' ] [-1 ] / portf_val [ 'Total Pos' ] [ 0 ] -1)
print('Your cumulative return was {:.2f}% '.format(cumulative_return))
print('Your investment grew to {:.2f} dollars '.format(cumulative_return/100 *100000 + 100000))

portf_val.tail(1)

portf_val['Daily Return'] = portf_val['Total Pos'].pct_change(1)

Sharpe_Ratio = portf_val['Daily Return'].mean() / portf_val['Daily Return'].std()

A_Sharpe_Ratio = (252**0.5) * Sharpe_Ratio
print (A_Sharpe_Ratio)

@app.route('/')
def test():
    #return jsonify(ticker)
    return jsonify({'walmart' : walmart},{'merck': merck},{'FSUVX' : FSUVX},{'nike': nike},{'axp' : axp},{'Proctor and Gamble' : pg},{'SOXX' : SOXX},{'starbucks' : starbucks},{'coka':coka},{'mdlz':mdlz})
    return walmart._json()
    return jsonify({'Sharpe Ratio' : A_Sharpe_Ratio},{'Cumulative Return (in %)' : cumulative_return})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port = 8090)