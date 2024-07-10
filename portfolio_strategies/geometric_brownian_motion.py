import matplotlib.pyplot as plt
import numpy as np
import math
import pandas_datareader.data as pdr
import pandas as pd
import datetime
from pylab import rcParams

# Define the parameters for fetching historical data
num_of_years = 5
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=int(355.25 * num_of_years))
stock = 'NIO'
index = '^GSPC'

# Fetching historical data from Yahoo Finance
stock_data = pdr.get_data_yahoo(stock, start_date, end_date)
index_data = pdr.get_data_yahoo(index, start_date, end_date)

# Resampling data to monthly frequency and calculating returns
stock_monthly = stock_data.resample('M').last()
index_monthly = index_data.resample('M').last()
combined_data = pd.DataFrame({'Stock': stock_monthly['Adj Close'], 
                              'Index': index_monthly['Adj Close']})
combined_returns = combined_data.pct_change().dropna()

# Calculating covariance matrix for the returns
cov_matrix = np.cov(combined_returns['Stock'], combined_returns['Index'])

# Class for Geometric Brownian Motion simulation
class GBM:
    def __init__(self, initial_price, drift, volatility, time_period, total_time):
        self.initial_price = initial_price
        self.drift = drift
        self.volatility = volatility
        self.time_period = time_period
        self.total_time = total_time
        self.simulate()

    def simulate(self):
        self.prices = [self.initial_price]
        while self.total_time > 0:
            dS = self.prices[-1] * (self.drift * self.time_period + 
                                    self.volatility * np.random.normal(0, math.sqrt(self.time_period)))
            self.prices.append(self.prices[-1] + dS)
            self.total_time -= self.time_period

# Parameters for GBM simulation
num_simulations = 20
initial_price = stock_data['Adj Close'][-1]
drift = 0.24
volatility = math.sqrt(cov_matrix[0, 0])
time_period = 1 / 365
total_time = 1

# Running multiple GBM simulations
simulations = [GBM(initial_price, drift, volatility, time_period, total_time) for _ in range(num_simulations)]

# Plotting the simulations
rcParams['figure.figsize'] = 15, 10
for sim in simulations:
    plt.plot(sim.prices)

plt.title(f'Geometric Brownian Motion for {stock.upper()}')
plt.axhline(y=initial_price, color='r', linestyle='--')
plt.xlabel('Time Steps')
plt.ylabel('Price')
plt.show()