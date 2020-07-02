import robin_stocks as r
import pandas as pd
from datetime import datetime
from config import *
import numpy as np

r.login(rh_username,rh_password)
my_stocks = r.build_holdings()

df = pd.DataFrame(my_stocks)
print(df)

df = df.T
df['ticker'] = df.index
df = df.reset_index(drop=True)

cols = df.columns.drop(['id','type','name','pe_ratio','ticker'])
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

df_buy = df[(df['average_buy_price'] <= 25.000) & (df['quantity'] == 1.000000) & (df['percent_change'] <= -.50)]
df_sell = df[(df['quantity'] == 5.000000) & (df['percent_change'] >= .50)]

print(df_buy)
print(df_sell)

tkr_buy_list  = df_buy['ticker'].tolist()
tkr_sell_list = df_sell['ticker'].tolist()

print(f"{len(r.orders.get_all_open_orders())} open order") 

r.orders.cancel_all_open_orders()

if len(tkr_sell_list) > 0:
    for i in tkr_sell_list:
        print(i)
        print(r.orders.order_sell_market(i,4,timeInForce= 'gfd'))
else:
    print('Nothing to sell right now!')


if len(tkr_buy_list) > 0:
    for i in tkr_buy_list:
        test = r.orders.order_buy_market(i,4,timeInForce= 'gfd')
        print(i)
        print(test)
        print(type(test))
else:
    print('Nothing to buy right now!')

r.get_crypto_currency_pairs()

r.stocks.get_earnings('TSLA',info='report')