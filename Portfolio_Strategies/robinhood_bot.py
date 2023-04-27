# Import necessary libraries
import robin_stocks as r
import pandas as pd
from datetime import datetime
import numpy as np

# Set options to display all columns of dataframes
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Log in to Robinhood account
r.login('rh_username','rh_password')

# Get holdings data
my_stocks = r.build_holdings()

# Create dataframe of holdings data and display it
df = pd.DataFrame(my_stocks)
print(df)

# Transpose dataframe and add a new column for ticker symbols
df = df.T
df['ticker'] = df.index

# Reset index to use numbered rows instead of ticker symbols as index
df = df.reset_index(drop=True)

# Convert appropriate columns to numeric data types
cols = df.columns.drop(['id','type','name','pe_ratio','ticker'])
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

# Filter dataframe to find stocks to buy and sell based on certain criteria
df_buy = df[(df['average_buy_price'] <= 25.000) & (df['quantity'] == 1.000000) & (df['percent_change'] <= -.50)]
df_sell = df[(df['quantity'] == 5.000000) & (df['percent_change'] >= .50)]

# Display filtered dataframes
print(df_buy)
print(df_sell)

# Create lists of tickers to buy and sell
tkr_buy_list  = df_buy['ticker'].tolist()
tkr_sell_list = df_sell['ticker'].tolist()

# Cancel all open orders
print(f"{len(r.orders.get_all_open_orders())} open order")
r.orders.cancel_all_open_orders()

# Sell stocks in sell list if any
if len(tkr_sell_list) > 0:
    for i in tkr_sell_list:
        print(i)
        print(r.orders.order_sell_market(i,4,timeInForce= 'gfd'))
else:
    print('Nothing to sell right now!')

# Buy stocks in buy list if any
if len(tkr_buy_list) > 0:
    for i in tkr_buy_list:
        test = r.orders.order_buy_market(i,4,timeInForce= 'gfd')
        print(i)
        print(test)
        print(type(test))
else:
    print('Nothing to buy right now!')

# Get cryptocurrency pairs and stock earnings data for TSLA
r.get_crypto_currency_pairs()
r.stocks.get_earnings('TSLA',info='report')