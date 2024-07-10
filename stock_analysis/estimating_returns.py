import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import datetime as dt
from pandas_datareader import DataReader

# Fetches stock data and calculates annual returns.
def get_stock_returns(ticker, start_date, end_date):
    stock_data = DataReader(ticker, 'yahoo', start_date, end_date)
    stock_data = stock_data.reset_index()
    open_prices = stock_data['Open'].tolist()
    open_prices = open_prices[::253]  # Annual data, assuming 253 trading days per year
    df_returns = pd.DataFrame({'Open': open_prices})
    df_returns['Return'] = df_returns['Open'].pct_change()
    return df_returns.dropna()

# Plots the normal distribution of returns.
def plot_return_distribution(returns, ticker):
    x = np.linspace(min(returns), max(returns), 100)
    mean, std = np.mean(returns), np.std(returns)
    plt.plot(x, norm.pdf(x, mean, std))
    plt.title(f'Normal Distribution of Returns for {ticker.upper()}')
    plt.xlabel('Returns')
    plt.ylabel('Frequency')
    plt.show()

# Estimates the probability of returns falling within specified bounds.
def estimate_return_probability(returns, lower_bound, higher_bound):
    mean, std = np.mean(returns), np.std(returns)
    prob = round(norm(mean, std).cdf(higher_bound) - norm(mean, std).cdf(lower_bound), 4)
    return prob

def main():
    stock_ticker = 'AAPL'
    higher_bound, lower_bound = 0.3, 0.2
    num_of_years = 40

    # Calculate start and end dates
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=int(365.25 * num_of_years))

    # Retrieve and process stock data
    df_returns = get_stock_returns(stock_ticker, start_date, end_date)
    plot_return_distribution(df_returns['Return'], stock_ticker)

    # Estimate probability
    prob = estimate_return_probability(df_returns['Return'], lower_bound, higher_bound)
    print(f'The probability of returns falling between {lower_bound} and {higher_bound} for {stock_ticker.upper()} is: {prob}')

if __name__ == "__main__":
    main()