# Import dependencies
import matplotlib.pyplot as plt
import numpy as np
import math
import yahoo_fin.stock_info as si
from pandas_datareader import DataReader
import pandas as pd
import datetime
from pylab import rcParams

# Define the number of years to go back in time to fetch data
num_of_years = 5

# Set the start and end dates for fetching data
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=int(355.25*num_of_years))

# Set the stock and index symbols to fetch data for
stock = 'NIO'
index = '^GSPC'

# Fetch stock and index data from Yahoo Finance
df = DataReader(stock, 'yahoo', start_date, end_date)
dfb = DataReader(index, 'yahoo', start_date, end_date)

# Resample the data to monthly frequency
rts = df.resample('M').last()
rbts = dfb.resample('M').last()

# Create a dataframe with adjusted close prices for the stock and index
dfsm = pd.DataFrame({'s_adjclose': rts['Adj Close'], 'b_adjclose': rbts['Adj Close']}, index=rts.index)

# Calculate the monthly returns for the stock and index
dfsm[['s_returns', 'b_returns']] = dfsm[['s_adjclose', 'b_adjclose']] / dfsm[['s_adjclose', 'b_adjclose']].shift(1) - 1

# Drop rows with missing data
dfsm = dfsm.dropna()

# Calculate the covariance matrix of the monthly returns
covmat = np.cov(dfsm['s_returns'], dfsm['b_returns'])

class GBM:
    def __init__(self, initial_price, drift, volatility, time_period, total_time):
        # Initialize fields
        self.initial_price = initial_price
        self.current_price = initial_price
        self.drift = drift
        self.volatility = volatility
        self.time_period = time_period
        self.total_time = total_time
        self.prices = []
        # Simulate the diffusion process
        self.simulate()

    def simulate(self):
        while self.total_time > 0:
            # Calculate the change in the stock price using the Geometric Brownian Motion formula
            dS = self.current_price * self.drift * self.time_period + \
                self.current_price * self.volatility * np.random.normal(0, math.sqrt(self.time_period))
            # Update the stock price
            self.prices.append(self.current_price + dS)
            self.current_price += dS
            self.total_time -= self.time_period

# Set the parameters for the Geometric Brownian Motion simulation
n = 20 # Number of simulations
initial_price = si.get_live_price(stock) # Use the live stock price as the initial price
drift = .24 # Use a constant drift value
volatility = np.sqrt(covmat[0,0]) # Use the volatility of the stock
time_period = 1 / 365 # Daily
total_time = 1 # 1 day

# Run the Geometric Brownian Motion simulation n times
simulations = [GBM(initial_price, drift, volatility, time_period, total_time) for i in range(n)]

# Plot the results
rcParams['figure.figsize'] = 15, 10 
for sim in simulations:
    plt.plot(np.arange(0, len(sim.prices)), sim.prices)

# Add the title, legend, and axis labels
plt.title(f'Geometric Brownian Motion for {stock.upper()}')
plt.axhline(y=si.get_live_price(stock), color='r')
plt.xlabel('Time')
plt.ylabel('Price')
plt.show()