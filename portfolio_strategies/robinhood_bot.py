import robin_stocks as r
import pandas as pd
from datetime import datetime
import numpy as np

# Setting display options for pandas DataFrames
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Log in to Robinhood account (replace with your username and password)
r.login('rh_username', 'rh_password')

# Fetch holdings data and convert it into a DataFrame
my_stocks = r.build_holdings()
df = pd.DataFrame(my_stocks).T  # Transpose to get tickers as rows
df['ticker'] = df.index  # Add ticker symbols as a column
df = df.reset_index(drop=True)  # Reset index

# Convert numeric columns to appropriate data types
numeric_cols = df.columns.drop(['id', 'type', 'name', 'pe_ratio', 'ticker'])
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Criteria for selecting stocks to buy and sell
buy_criteria = (df['average_buy_price'] <= 25.00) & (df['quantity'] == 1.00) & (df['percent_change'] <= -0.50)
sell_criteria = (df['quantity'] == 5.00) & (df['percent_change'] >= 0.50)

# Filter DataFrame based on criteria
df_buy = df[buy_criteria]
df_sell = df[sell_criteria]

# Display filtered DataFrames
print(df_buy)
print(df_sell)

# Create lists of tickers to buy and sell
tickers_to_buy = df_buy['ticker'].tolist()
tickers_to_sell = df_sell['ticker'].tolist()

# Cancel all open orders
open_orders = r.orders.get_all_open_orders()
print(f"{len(open_orders)} open order(s)")
r.orders.cancel_all_open_orders()

# Sell stocks based on the sell list
if tickers_to_sell:
    for ticker in tickers_to_sell:
        sell_order = r.orders.order_sell_market(ticker, 4, timeInForce='gfd')
        print(f"Selling {ticker}: {sell_order}")
else:
    print('Nothing to sell right now!')

# Buy stocks based on the buy list
if tickers_to_buy:
    for ticker in tickers_to_buy:
        buy_order = r.orders.order_buy_market(ticker, 4, timeInForce='gfd')
        print(f"Buying {ticker}: {buy_order}")
else:
    print('Nothing to buy right now!')

# Additional data retrieval: Cryptocurrency pairs and TSLA stock earnings
crypto_pairs = r.get_crypto_currency_pairs()
tsla_earnings = r.stocks.get_earnings('TSLA', info='report')