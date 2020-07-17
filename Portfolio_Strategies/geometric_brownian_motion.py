import matplotlib.pyplot as plt
import numpy as np
import math
import yahoo_fin.stock_info as si
from pandas_datareader import DataReader
import pandas as pd
import datetime
from pylab import rcParams
from yahoo_fin import stock_info as si

num_of_years = 5
start_date = datetime.datetime.now() - datetime.timedelta(days=int(355.25*5))
end_date = datetime.date.today()

stock = 'NIO'
index = '^GSPC'

df = DataReader(stock,'yahoo', start_date, end_date)
dfb = DataReader(index,'yahoo', start_date, end_date)

rts = df.resample('M').last()
rbts = dfb.resample('M').last()
dfsm = pd.DataFrame({'s_adjclose' : rts['Adj Close'],
                        'b_adjclose' : rbts['Adj Close']},
                        index=rts.index)

dfsm[['s_returns','b_returns']] = dfsm[['s_adjclose','b_adjclose']]/\
    dfsm[['s_adjclose','b_adjclose']].shift(1) -1
dfsm = dfsm.dropna()
covmat = np.cov(dfsm["s_returns"],dfsm["b_returns"])

class GBM:

    def simulate(self):
        while(self.total_time > 0):
            dS = self.current_price*self.drift*self.time_period + self.current_price*self.volatility*np.random.normal(0, math.sqrt(self.time_period))
            self.prices.append(self.current_price + dS)
            self.current_price += dS
            self.total_time -= self.time_period

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
        self.simulate()   # Simulate the diffusion proces

simulations = []
n = 20
initial_price = si.get_live_price(stock)
drift = .24
volatility = np.sqrt(covmat[0,0])
time_period = 1/365 # Daily
total_time = 1

for i in range(0, n):
    simulations.append(GBM(initial_price, drift, volatility, time_period, total_time))

rcParams['figure.figsize'] = 15, 10 
for sim in simulations:
    plt.plot(np.arange(0, len(sim.prices)), sim.prices)

plt.title(f'Geometric Brownian Motion for {stock.upper()}')
plt.axhline(y=si.get_live_price(stock), color='r')
plt.xlabel('Time')
plt.ylabel('Price')
plt.show()