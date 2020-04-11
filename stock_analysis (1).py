from pandas_datareader import DataReader
import numpy as np
import pandas as pd

# Grab time series data for 5-year history for the stock (here AAPL)
# and for S&P-500 Index
df = DataReader('MRK','yahoo','2018-07-30', '2019-07-30')
dfb = DataReader('^GSPC','yahoo','2018-07-30', '2019-07-30')

# create a time-series of monthly data points
rts = df.resample('M').last()
rbts = dfb.resample('M').last()
dfsm = pd.DataFrame({'s_adjclose' : rts['Adj Close'],
                        'b_adjclose' : rbts['Adj Close']},
                        index=rts.index)

# compute returns
dfsm[['s_returns','b_returns']] = dfsm[['s_adjclose','b_adjclose']]/\
    dfsm[['s_adjclose','b_adjclose']].shift(1) -1
dfsm = dfsm.dropna()
covmat = np.cov(dfsm["s_returns"],dfsm["b_returns"])

# calculate measures now
beta = covmat[0,1]/covmat[1,1]
alpha= np.mean(dfsm["s_returns"])-beta*np.mean(dfsm["b_returns"])

# r_squared     = 1. - SS_res/SS_tot
ypred = alpha + beta * dfsm["b_returns"]
SS_res = np.sum(np.power(ypred-dfsm["s_returns"],2))
SS_tot = covmat[0,0]*(len(dfsm)-1) # SS_tot is sample_variance*(n-1)
r_squared = 1. - SS_res/SS_tot
# 5- year volatiity and 1-year momentum
volatility = np.sqrt(covmat[0,0])
momentum = np.prod(1+dfsm["s_returns"].tail(12).values) -1

# annualize the numbers
prd = 12. # used monthly returns; 12 periods to annualize
alpha = alpha*prd
volatility = volatility*np.sqrt(prd)

print (f'beta = {beta}')
print (f'alpha = {alpha}')
print (f'r_squared = {r_squared}')
print (f'volatility = {volatility}')
print (f'momentum = {momentum}')
