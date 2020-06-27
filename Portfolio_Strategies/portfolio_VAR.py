import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as web
from matplotlib.ticker import FuncFormatter
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from matplotlib.ticker import FuncFormatter
from pypfopt import objective_functions, base_optimizer
from scipy.stats import norm
import math
import datetime as dt

tickers = ['GOOGL','FB','AAPL','NFLX','AMZN']
Time=1440 #No of days(steps or trading days in this case)
pvalue = 1000 #portfolio value

num_of_years = 3
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 

length = len(tickers)
price_data = []

for ticker in range(length):
   prices = web.DataReader(tickers[ticker], start = start_date, end = end_date, data_source='yahoo')
   price_data.append(prices[['Adj Close']])

df_stocks = pd.concat(price_data, axis=1)
df_stocks.columns=tickers

mu = expected_returns.mean_historical_return(df_stocks)
Sigma = risk_models.sample_cov(df_stocks)
ef = EfficientFrontier(mu, Sigma, weight_bounds=(0,1)) 
sharpe_pfolio=ef.max_sharpe() 
sharpe_pwt=ef.clean_weights()
print(sharpe_pwt)

#VaR Calculation
ticker_rx2 = []
sh_wt = list(sharpe_pwt.values())
sh_wt=np.array(sh_wt)

for a in range(length):
    ticker_rx = df_stocks[[tickers[a]]].pct_change()
    ticker_rx = (ticker_rx+1).cumprod()
    ticker_rx2.append(ticker_rx[[tickers[a]]])
ticker_final = pd.concat(ticker_rx2,axis=1)

#Plot graph of Cumulative/HPR of all stocks
for i, col in enumerate(ticker_final.columns):
  ticker_final[col].plot()
plt.title('Cumulative Returns')
plt.xticks(rotation=80)
plt.legend(ticker_final.columns)
plt.subplots()
plt.show()

#Taking Latest Values of Return
pret = []
pre1 = []
price =[]
for x in range(length):
    pret.append(ticker_final.iloc[[-1],[x]])
    price.append((df_stocks.iloc[[-1],[x]]))
pre1 = pd.concat(pret,axis=1)
pre1 = np.array(pre1)
price = pd.concat(price,axis=1)
varsigma = pre1.std()
ex_rtn=pre1.dot(sh_wt)
price=price.dot(sh_wt) 
#ex_rtn = (ex_rtn)**0.5-(1)

print('The weighted expected portfolio return for selected time period is: '+ str(ex_rtn[0]))
print ('The var sigma is: ' + str(varsigma))
print ('The price is: ' + str(price))

lt_price=[]
final_res=[]
daily_returns = []

for i in range(10000): 
    daily_return = (np.random.normal(ex_rtn/Time,varsigma/math.sqrt(Time),Time))
    daily_returns.append(daily_return)

plt.plot(daily_returns)
plt.title(f'Range of returns in a day of {Time} minutes')
plt.axhline(np.percentile(daily_returns,5), color='r', linestyle='dashed', linewidth=1)
plt.axhline(np.percentile(daily_returns,95), color='g', linestyle='dashed', linewidth=1)
plt.axhline(np.mean(daily_returns), color='b', linestyle='solid', linewidth=1)
plt.subplots()
plt.show()

plt.hist(daily_returns,bins=15)
plt.axvline(np.percentile(daily_returns,5), color='r', linestyle='dashed', linewidth=2)
plt.axvline(np.percentile(daily_returns,95), color='r', linestyle='dashed', linewidth=2)
plt.subplots()
plt.show()

print(np.percentile(daily_returns,5),np.percentile(daily_returns,95))
print('$Amount required to cover minimum losses for one day is ' + str(pvalue* - np.percentile(daily_returns,5)))