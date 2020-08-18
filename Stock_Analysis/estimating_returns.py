# imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import datetime as dt
from pandas_datareader import DataReader
import warnings

warnings.filterwarnings('ignore')

# parameters
stock = 'AAPL'
higher_bound = 0.3
lower_bound= 0.2

num_of_years = 40
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 

# data
df = DataReader(stock, 'yahoo', start_date, end_date)
df = df.reset_index()

# returns
open_prices1 = []
i = 0
while i < len(df['Close'].tolist()):
    data = df['Open'].iloc[i]
    open_prices1.append(data)
    i += 253
    
df_returns = pd.DataFrame({'Open': open_prices1})

df_returns['Return'] = df_returns['Open'].pct_change()
df_returns = df_returns.dropna()
returns = list(df_returns['Return'])

# plot normal distribution
x = np.linspace(df_returns['Return'].min(), 1, 100)
mean = np.mean(returns)
std = np.std(returns)
norm_dist = norm.pdf(x, mean, std)
plt.plot(x, norm_dist)
plt.title(f'Normal Distribution of Returns for {stock.upper()}')
plt.xlabel('Returns')
plt.ylabel('Frequency')
plt.show()

# estimate the probability of returns falling between lower_bound and higher_bound
norm_cdf = norm(mean, std).cdf
print(f'The probability of returns falling between {lower_bound} and {higher_bound} for {stock.upper()} is: ', round(norm_cdf(higher_bound) - norm_cdf(lower_bound), 4))
