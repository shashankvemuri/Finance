import pandas_datareader.data as pdr
import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np

# Function to fetch stock data
def get_stock_data(stock, start, end):
    """
    Fetches stock data from Yahoo Finance.
    """
    return pdr.get_data_yahoo(stock, start, end)

# Trading statistics calculation
def calculate_trading_statistics(df, buy_sell_logic, additional_logic=None):
    """
    Calculates trading statistics based on buy/sell logic.
    """
    position = 0
    percentChange = []
    for i in df.index:
        close = df.loc[i, "Adj Close"]
        if buy_sell_logic(df, i, position):
            position = 0 if position == 1 else 1
            buyP = close if position == 1 else buyP
            sellP = close if position == 0 else sellP
            if position == 0:
                perc = (sellP / buyP - 1) * 100
                percentChange.append(perc)
        if additional_logic: additional_logic(df, i)
    return calculate_statistics_from_percent_change(percentChange)

# Compute statistics from percent change
def calculate_statistics_from_percent_change(percentChange):
    """
    Computes statistics from percentage change in stock prices.
    """
    gains = sum(p for p in percentChange if p > 0)
    losses = sum(p for p in percentChange if p < 0)
    numGains = sum(1 for p in percentChange if p > 0)
    numLosses = sum(1 for p in percentChange if p < 0)
    totReturn = round(np.prod([((p / 100) + 1) for p in percentChange]) * 100 - 100, 2)
    avgGain = gains / numGains if numGains > 0 else 0
    avgLoss = losses / numLosses if numLosses > 0 else 0
    maxReturn = max(percentChange) if numGains > 0 else 0
    maxLoss = min(percentChange) if numLosses > 0 else 0
    ratioRR = -avgGain / avgLoss if numLosses > 0 else "inf"
    batting_avg = numGains / (numGains + numLosses) if numGains + numLosses > 0 else 0
    return {
        "total_return": totReturn,
        "avg_gain": avgGain,
        "avg_loss": avgLoss,
        "max_return": maxReturn,
        "max_loss": maxLoss,
        "gain_loss_ratio": ratioRR,
        "num_trades": numGains + numLosses,
        "batting_avg": batting_avg
    }

# SMA strategy logic
def sma_strategy_logic(df, i, position):
    """
    Logic for Simple Moving Average (SMA) trading strategy.
    """
    SMA_short, SMA_long = df["SMA_20"], df["SMA_50"]
    return (SMA_short[i] > SMA_long[i] and position == 0) or (SMA_short[i] < SMA_long[i] and position == 1)

# Main program
def main():
    """
    Main program to test trading strategies.
    """
    stock = input("Enter a stock ticker: ")
    num_of_years = float(input("Enter number of years: "))
    start = dt.datetime.now() - dt.timedelta(days=365.25 * num_of_years)
    end = dt.datetime.now()
    df = get_stock_data(stock, start, end)

    # Implementing SMA strategy
    df["SMA_20"] = df["Adj Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Adj Close"].rolling(window=50).mean()
    sma_stats = calculate_trading_statistics(df, sma_strategy_logic)
    print("Simple Moving Average Strategy Stats:", sma_stats)

if __name__ == "__main__":
    main()