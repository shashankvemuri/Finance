import pandas_datareader as web
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Function to download stock data
def download_data(symbol, source, start, end):
    start = datetime.strptime(start, '%d-%m-%Y')
    end = datetime.strptime(end, '%d-%m-%Y')
    df = web.DataReader(symbol, data_source=source, start=start, end=end)
    return df

# Function to calculate annual volatility
def annual_volatility(df):
    quote = df['Close']
    returns = quote.pct_change()
    return returns.std() * np.sqrt(252)

# Function to calculate CAGR
def cagr(df):
    quote = df['Close']
    days = (quote.index[-1] - quote.index[0]).days
    return ((((quote[-1]) / quote[1])) ** (365.0/days)) - 1

# Monte Carlo Simulation Function
def monte_carlo_simulation(symbol, source, start, end, simulations, days_predicted):
    df = download_data(symbol, source, start, end)
    mu = cagr(df)
    vol = annual_volatility(df)
    start_price = df['Close'][-1]

    results = []
    plt.figure(figsize=(10, 6))
    
    # Run simulations
    for _ in range(simulations):
        prices = [start_price]
        for _ in range(days_predicted):
            shock = np.random.normal(mu / days_predicted, vol / math.sqrt(days_predicted))
            prices.append(prices[-1] * (1 + shock))
        plt.plot(prices)
        results.append(prices[-1])

    plt.title(f"{symbol} Monte Carlo Simulation")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.show()

    return pd.DataFrame({
        "Results": results,
        "Percentile 5%": np.percentile(results, 5),
        "Percentile 95%": np.percentile(results, 95)
    })

# Main function
def main():
    symbol = 'NIO'
    start_date = '01-01-2015'
    end_date = '01-01-2020'
    simulations = 1000
    days_predicted = 252

    # Perform Monte Carlo Simulation
    simulation_results = monte_carlo_simulation(symbol, 'yahoo', start_date, end_date, simulations, days_predicted)
    print(simulation_results)

if __name__ == "__main__":
    main()