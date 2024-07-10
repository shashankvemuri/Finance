# Importing necessary libraries
import pandas as pd
import datetime as dt
from pandas_datareader import data as pdr
import yfinance as yf

# Override yfinance with pandas datareader
yf.pdr_override()

# Define the stock symbol to analyze
stock = 'AAPL'

# Function to retrieve stock data for a specified period
def get_symbol(symbol):
    # Define time range for data retrieval (1 year)
    num_of_years = 1
    start_date = dt.date.today() - dt.timedelta(days=365 * num_of_years)
    end_date = dt.date.today()

    # Fetch the stock data
    df = pdr.get_data_yahoo(symbol, start_date, end_date)
    return df

# Function to calculate VWAP (Volume Weighted Average Price)
def VWAP():
    df = get_symbol(stock)

    # Calculate typical price
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Adj Close']) / 3
    df['TP_Volume'] = df['Typical_Price'] * df['Volume']

    # Calculate VWAP
    cumulative_TP_V = df['TP_Volume'].sum()
    cumulative_V = df['Volume'].sum()
    vwap = cumulative_TP_V / cumulative_V
    return vwap

# Displaying the VWAP for the specified stock
print("VWAP: ", VWAP())

# Function to update VWAP with a different method
def update_VWAP():
    df = get_symbol(stock)

    # Calculate weighted prices
    df['OpenxVolume'] = df['Open'] * df['Volume']
    df['HighxVolume'] = df['High'] * df['Volume']
    df['LowxVolume'] = df['Low'] * df['Volume']
    df['ClosexVolume'] = df['Adj Close'] * df['Volume']

    # Calculate VWAP components
    sum_volume = df['Volume'].sum()
    sum_x_OV = df['OpenxVolume'].sum() / sum_volume
    sum_x_HV = df['HighxVolume'].sum() / sum_volume
    sum_x_LV = df['LowxVolume'].sum() / sum_volume
    sum_x_CV = df['ClosexVolume'].sum() / sum_volume
    average_volume_each = (sum_x_OV + sum_x_HV + sum_x_LV + sum_x_OV) / 4

    # Calculate updated VWAP
    new_vwap = ((df['Adj Close'][-1] - average_volume_each) + (df['Adj Close'][-1] + average_volume_each)) / 2
    return new_vwap

# Display the updated VWAP
print("Updated VWAP: ", update_VWAP())

# Function to add a VWAP column to the stock data
def add_VWAP_column():
    df = get_symbol(stock)

    # Calculate weighted prices
    df['OpenxVolume'] = df['Open'] * df['Volume']
    df['HighxVolume'] = df['High'] * df['Volume']
    df['LowxVolume'] = df['Low'] * df['Volume']
    df['ClosexVolume'] = df['Adj Close'] * df['Volume']

    # Calculate and add the VWAP column
    vwap_column = (df[['OpenxVolume', 'HighxVolume', 'LowxVolume', 'ClosexVolume']].mean(axis=1)) / df['Volume']
    df['VWAP'] = vwap_column
    return df

# Print the stock data with the added VWAP column
print(add_VWAP_column())