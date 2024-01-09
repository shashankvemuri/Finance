import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
import datetime as dt
import sys
import os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import ta_functions as ta

# Set display options for pandas DataFrame
pd.set_option("display.max_columns", None)

# Function to get stock data
def get_stock_data(stock, start, end):
    return pdr.get_data_yahoo(stock, start, end)

# Function to calculate trading statistics
def calculate_trading_statistics(df, start, buy_sell_logic, additional_logic=None):
    position = 0
    percentChange = []
    for i in df.index:
        close = df["Adj Close"][i]
        if buy_sell_logic(df, i, position):
            if position == 0:
                buyP = close
                position = 1
            elif position == 1:
                position = 0
                sellP = close
                perc = (sellP / buyP - 1) * 100
                percentChange.append(perc)
        if additional_logic:
            additional_logic(df, i)
    return calculate_statistics_from_percent_change(percentChange, start)

# Function to compute statistics from percent change
def calculate_statistics_from_percent_change(percentChange, start):
    gains, losses, numGains, numLosses, totReturn = 0, 0, 0, 0, 1
    for i in percentChange:
        if i > 0:
            gains += i
            numGains += 1
        else:
            losses += i
            numLosses += 1
        totReturn *= ((i / 100) + 1)
    totReturn = round((totReturn - 1) * 100, 2)
    return extract_trade_statistics(gains, losses, numGains, numLosses, percentChange, totReturn, start)

# Function to extract trade statistics
def extract_trade_statistics(gains, losses, numGains, numLosses, percentChange, totReturn, start):
    avgGain, avgLoss, maxReturn, maxLoss, ratioRR = 0, 0, "nan", "nan", "inf"
    if numGains > 0:
        avgGain = gains / numGains
        maxReturn = max(percentChange)
    if numLosses > 0:
        avgLoss = losses / numLosses
        maxLoss = min(percentChange)
        ratioRR = -avgGain / avgLoss if avgLoss != 0 else "inf"
    return {
        "start": start,
        "total_return": totReturn,
        "avg_gain": avgGain,
        "avg_loss": avgLoss,
        "max_return": maxReturn,
        "max_loss": maxLoss,
        "gain_loss_ratio": ratioRR,
        "num_trades": numGains + numLosses,
        "batting_avg": numGains / (numGains + numLosses) if numGains + numLosses > 0 else 0
    }

# Logic for SMA strategy
def sma_strategy_logic(df, i, position):
    SMA_short, SMA_long = df["SMA_20"], df["SMA_50"]
    return (SMA_short[i] > SMA_long[i] and position == 0) or (SMA_short[i] < SMA_long[i] and position == 1)

# Initialize main program
def main():
    stock = input("Enter a stock ticker: ")
    num_of_years = float(input("Enter number of years: "))

    start = dt.date.today() - dt.timedelta(days=int(365.25 * num_of_years))
    end = dt.datetime.now()

    df = get_stock_data(stock, start, end)

    # SMA strategy implementation
    short_sma, long_sma = 20, 50
    df["SMA_20"] = df.iloc[:, 4].rolling(window=short_sma).mean()
    df["SMA_50"] = df.iloc[:, 4].rolling(window=long_sma).mean()
    sma_stats = calculate_trading_statistics(df, start, sma_strategy_logic)
    print("Simple Moving Average Strategy Stats:", sma_stats)

    # Add other strategies similarly using their respective logic functions

# Run the program
if __name__ == "__main__":
    main()