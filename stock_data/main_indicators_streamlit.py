import yfinance as yf
import pandas_datareader.data as pdr
import streamlit as st
import datetime
import matplotlib.pyplot as plt
import ta
import pandas as pd
import requests
import sys
import os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import ta_functions as ta

# Override default pandas datareader's Yahoo Finance method
yf.pdr_override()

# Streamlit web app title and description
st.write(
    """
    # Technical Analysis Web Application
    Shown below are the Moving Average Crossovers, Bollinger Bands,
    MACD's, Commodity Channel Indexes, Relative Strength Indexes
    and Extended Market Calculators of any stock!
    """
)

# Sidebar for user input
st.sidebar.header("User Input Parameters")
today = datetime.date.today()

def user_input_features():
    # Sidebar input fields for ticker and date range
    ticker = st.sidebar.text_input("Ticker", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2019-01-01")
    end_date = st.sidebar.text_input("End Date", str(today))
    return ticker, start_date, end_date

symbol, start, end = user_input_features()

# Convert string dates to datetime objects
start = pd.to_datetime(start)
end = pd.to_datetime(end)

# Download stock data from Yahoo Finance
data = pdr.get_data_yahoo(symbol, start, end)

# Display Adjusted Close Price
st.header(f"Adjusted Close Price\n {symbol}")
st.line_chart(data["Adj Close"])

# Calculate and display SMA and EMA
data["SMA"] = ta.SMA(data["Adj Close"], timeperiod=20)
data["EMA"] = ta.EMA(data["Adj Close"], timeperiod=20)
st.header(f"Simple Moving Average vs. Exponential Moving Average\n {symbol}")
st.line_chart(data[["Adj Close", "SMA", "EMA"]])

# Calculate and display Bollinger Bands
data["upper_band"], data["middle_band"], data["lower_band"] = ta.BBANDS(data["Adj Close"], timeperiod=20)
st.header(f"Bollinger Bands\n {symbol}")
st.line_chart(data[["Adj Close", "upper_band", "middle_band", "lower_band"]])

# Calculate and display MACD
data["macd"], data["macdsignal"], data["macdhist"] = ta.MACD(data["Adj Close"], fastperiod=12, slowperiod=26, signalperiod=9)
st.header(f"Moving Average Convergence Divergence\n {symbol}")
st.line_chart(data[["macd", "macdsignal"]])

# Calculate and display CCI
data["CCI"] = ta.CCI(data["High"], data["Low"], data["Close"], timeperiod=14)
st.header(f"Commodity Channel Index\n {symbol}")
st.line_chart(data["CCI"])

# Calculate and display RSI
data["RSI"] = ta.RSI(data["Adj Close"], timeperiod=14)
st.header(f"Relative Strength Index\n {symbol}")
st.line_chart(data["RSI"])

# Calculate and display OBV
data["OBV"] = ta.OBV(data["Adj Close"], data["Volume"]) / 10**6
st.header(f"On Balance Volume\n {symbol}")
st.line_chart(data["OBV"])