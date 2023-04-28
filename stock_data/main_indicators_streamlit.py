# Import dependencies
import yfinance as yf
import streamlit as st
import datetime
import matplotlib.pyplot as plt
import talib
import ta
import numpy as np
import pandas as pd
import requests

# Override pandas datareader's get_data_yahoo() function
yf.pdr_override()

# Application title and description
st.write(
    """
# Technical Analysis Web Application
Shown below are the **Moving Average Crossovers**, **Bollinger Bands**,
**MACD's**, **Commodity Channel Indexes**, **Relative Strength Indexes**
and **Extended Market Calculators** of any stock!
"""
)

# User input parameters in the sidebar
st.sidebar.header("User Input Parameters")

today = datetime.date.today()

def user_input_features():
    ticker = st.sidebar.text_input("Ticker", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2019-01-01")
    end_date = st.sidebar.text_input("End Date", f"{today}")
    return ticker, start_date, end_date

symbol, start, end = user_input_features()

def get_symbol(symbol):
    """Returns the company name given the stock symbol using the Yahoo Finance API"""
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(
        symbol
    )
    result = requests.get(url).json()
    for x in result["ResultSet"]["Result"]:
        if x["symbol"] == symbol:
            return x["name"]

# Get company name from symbol
company_name = get_symbol(symbol.upper())

# Convert start and end dates to datetime objects
start = pd.to_datetime(start)
end = pd.to_datetime(end)

# Download stock data from Yahoo Finance API
data = yf.download(symbol, start, end)

# Adjusted Close Price chart
st.header(
    f"""
          Adjusted Close Price\n {company_name}
          """
)
st.line_chart(data["Adj Close"])

# Simple Moving Average and Exponential Moving Average charts
data["SMA"] = talib.SMA(data["Adj Close"], timeperiod=20)
data["EMA"] = talib.EMA(data["Adj Close"], timeperiod=20)

st.header(
    f"""
          Simple Moving Average vs. Exponential Moving Average\n {company_name}
          """
)
st.line_chart(data[["Adj Close", "SMA", "EMA"]])

# Bollinger Bands chart
data["upper_band"], data["middle_band"], data["lower_band"] = talib.BBANDS(
    data["Adj Close"], timeperiod=20
)

st.header(
    f"""
          Bollinger Bands\n {company_name}
          """
)
st.line_chart(data[["Adj Close", "upper_band", "middle_band", "lower_band"]])

# Moving Average Convergence Divergence (MACD) chart
data["macd"], data["macdsignal"], data["macdhist"] = talib.MACD(
    data["Adj Close"], fastperiod=12, slowperiod=26, signalperiod=9
)

st.header(
    f"""
          Moving Average Convergence Divergence\n {company_name}
          """
)
st.line_chart(data[["macd", "macdsignal"]])

# Commodity Channel Index (CCI) chart
cci = ta.trend.cci(data["High"], data["Low"], data["Close"], n=31, c=0.015)

st.header(
    f"""
          Commodity Channel Index\n {company_name}
          """
)
st.line_chart(cci)

# Relative Strength Index (RSI) Chart
data["RSI"] = talib.RSI(data["Adj Close"], timeperiod=14)

st.header(
    f"""
          Relative Strength Index\n {company_name}
          """
)
st.line_chart(data["RSI"])

# On Balance Volume (OBV) Chart
data["OBV"] = talib.OBV(data["Adj Close"], data["Volume"]) / 10**6

st.header(
    f"""
          On Balance Volume\n {company_name}
          """
)
st.line_chart(data["OBV"])