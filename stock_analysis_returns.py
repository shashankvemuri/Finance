# # Stock Analysis Returns
# Library
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt

start = dt.date.today() - dt.timedelta(days = 365*3)
end = dt.date.today()

market = 'SPY'
symbol1 = 'AAPL'
symbol2 = 'MSFT'
symbol3 = 'AMD'
symbol4 = 'INTC'
bench = yf.download(market, start=start, end=end)
stock1 = yf.download(symbol1, start=start, end=end)
stock2 = yf.download(symbol2, start=start, end=end)
stock3 = yf.download(symbol3, start=start, end=end)
stock4 = yf.download(symbol4, start=start, end=end)

# ## Calculate Daily Gains
#Daily gain for the stock
stock1["Gain"]=(stock1["Adj Close"].pct_change())*100
stock2["Gain"]=(stock2["Adj Close"].pct_change())*100
stock3["Gain"]=(stock3["Adj Close"].pct_change())*100
stock4["Gain"]=(stock4["Adj Close"].pct_change())*100


# ## Calculate the Mean and Variances of Daily Gains
print('Stock '+ symbol1 + ' Mean:', stock1["Gain"].mean())
print('Stock '+ symbol1 + ' Variances:', stock1["Gain"].var())

print('Stock '+ symbol2 + ' Mean:', stock2["Gain"].mean())
print('Stock '+ symbol2 + ' Variances:', stock2["Gain"].var())

print('Stock '+ symbol3 + ' Mean:', stock3["Gain"].mean())
print('Stock '+ symbol3 + ' Variances:', stock3["Gain"].var())

print('Stock '+ symbol4 + ' Mean:', stock4["Gain"].mean())
print('Stock '+ symbol4 + ' Variances:', stock4["Gain"].var())

# ## Highest volatality and draw the histogram distribution of daily returns for all the stock
sns.set(rc={"figure.figsize": (15, 10)});
sns.distplot(stock1['Gain'], hist = False, color = 'b' )
sns.distplot(stock2['Gain'], hist = False, color = 'r' )
sns.distplot(stock3['Gain'], hist = False, color = 'g' )
sns.distplot(stock4['Gain'], hist = False, color = 'y' )

# ## Correlation
All_Stocks = pd.concat([stock1['Gain'],stock2['Gain'],stock3['Gain'],stock4['Gain']], axis=1)

names = [symbol1, symbol2, symbol3, symbol4]
All_Stocks.columns = names
All_Stocks = All_Stocks.dropna()

print (All_Stocks.corr())

#Heat map
sns.set(rc={"figure.figsize": (6, 4)});
sns.heatmap( All_Stocks.corr())

# ### Monthly Returns
Stock1_Monthly = stock1.asfreq('M').ffill()
Stock2_Monthly = stock2.asfreq('M').ffill()
Stock3_Monthly = stock3.asfreq('M').ffill()
Stock4_Monthly = stock4.asfreq('M').ffill()

print('Monthly Returns')
print('Stock '+ symbol1 + ' Mean:', Stock1_Monthly["Gain"].mean())
print('Stock '+ symbol1 + ' Variances:', Stock1_Monthly["Gain"].var())

print('Monthly Returns')
print('Stock '+ symbol2 + ' Mean:', Stock2_Monthly["Gain"].mean())
print('Stock '+ symbol2 + ' Variances:', Stock2_Monthly["Gain"].var())

print('Monthly Returns')
print('Stock '+ symbol3 + ' Mean:', Stock3_Monthly["Gain"].mean())
print('Stock '+ symbol3 + ' Variances:', Stock3_Monthly["Gain"].var())

print('Monthly Returns')
print('Stock '+ symbol4 + ' Mean:', Stock4_Monthly["Gain"].mean())
print('Stock '+ symbol4 + ' Variances:', Stock4_Monthly["Gain"].var())


# ## Monthly Returns with Box Plot
Stock1=np.array(Stock1_Monthly["Gain"])
Stock1= Stock1[~np.isnan(Stock1_Monthly["Gain"])]

Stock2 = np.array(Stock2_Monthly["Gain"])
Stock2=Stock2[~np.isnan(Stock2_Monthly["Gain"])]

Stock3 = np.array(Stock3_Monthly["Gain"])
Stock3=Stock3[~np.isnan(Stock3_Monthly["Gain"])]

Stock4 = np.array(Stock4_Monthly["Gain"])
Stock4=Stock4[~np.isnan(Stock4_Monthly["Gain"])]

AllStocks =[Stock1,Stock2,Stock3,Stock4]

fig = plt.figure(1, figsize=(20, 10))
ax = fig.add_subplot(111)
bp = ax.boxplot(AllStocks)
ax.set_xticklabels([symbol1, symbol2, symbol3, symbol4])


# ## Stock with highest probability gains with 2% or more
#Probability of Stock1
stock1_p = 1-stats.norm.cdf( 0.02,
             loc=Stock1_Monthly["Gain"].mean(),
             scale=Stock1_Monthly["Gain"].std())

print(symbol1 + " probability of gains:", round(stock1_p, 2))

stock2_p = 1-stats.norm.cdf( 0.02,
             loc=Stock2_Monthly["Gain"].mean(),
             scale=Stock2_Monthly["Gain"].std())

print(symbol2 + " probability of gains:", round(stock2_p, 2))

stock3_p = 1-stats.norm.cdf( 0.02,
             loc=Stock3_Monthly["Gain"].mean(),
             scale=Stock3_Monthly["Gain"].std())

print(symbol3 + " probability of gains:", round(stock3_p, 2))

stock4_p = 1-stats.norm.cdf( 0.02,
             loc=Stock4_Monthly["Gain"].mean(),
             scale=Stock4_Monthly["Gain"].std())

print(symbol4 + " probability of gains:", round(stock4_p, 2))


# ## Stock with highest probability of loss with 2% or more
#Probability of Stock1
stock1_l = stats.norm.cdf(-0.02,
             loc=Stock1_Monthly["Gain"].mean(),
             scale=Stock1_Monthly["Gain"].std())

print(symbol1 + " probability of loss:", round(stock1_l, 2))

stock2_l = stats.norm.cdf(-0.02,
             loc=Stock2_Monthly["Gain"].mean(),
             scale=Stock2_Monthly["Gain"].std())

print(symbol2 + " probability of loss:", round(stock2_l, 2))

stock3_l = stats.norm.cdf(-0.02,
             loc=Stock3_Monthly["Gain"].mean(),
             scale=Stock3_Monthly["Gain"].std())

print(symbol3 + " probability of loss:", round(stock3_l, 2))

stock4_l = stats.norm.cdf(-0.02,
             loc=Stock4_Monthly["Gain"].mean(),
             scale=Stock4_Monthly["Gain"].std())

print(symbol4 + " probability of loss:", round(stock4_l, 2))


# ## Portfolio Analysis
x=np.array([Stock1_Monthly["Gain"].mean(),Stock2_Monthly["Gain"].mean(),Stock3_Monthly["Gain"].mean(),Stock4_Monthly["Gain"].mean()])
print(x)

#Weights of the stocks is 0.25 which is added up to 1
weights = np.array([0.25,0.25,0.25,0.25])
exp_val=np.sum(x*weights)

print("Expected Value is ",round(exp_val,4))
print("\n")
#Calculate Covariance matrix
y = np.vstack([Stock1,Stock2,Stock3,Stock4])

cov = np.cov(y)
print("Below is covariance matrix")
print("\n")
print(cov)

#Calcualte the variance of monthly return of portfolio
covar=np.dot(weights.T,np.dot(cov,weights))
print("Variance of portfolio is ",round(covar,4))

#Calculate the probability
1-stats.norm.cdf(0.005,
             loc=exp_val,
             scale=covar)

# Create 25 Iteration of weights
# Generate a random number

number=range(1,26)

# Function to calculate expected value of portfolio and variance
def calculate(weights, meanReturns, covMatrix):
     
     portReturn = np.sum(weights*meanReturns)
     portVar = (np.dot(weights.T, np.dot(covMatrix, weights)))
     return portReturn, portVar

# Generate weights in random that sum to 1 
import random
random.seed(4)
d=[]
for i in number:
    weights = np.random.random(4)
    weights /= weights.sum()
    print("Set of random weight for Iterartion-->",i,"is", weights)
    pret, pvar = calculate(weights, x, cov)
    
    d.append((weights[0],weights[1],weights[2],weights[3],pret,pvar))
    df=pd.DataFrame(d,columns=('Stock1_weight','Stock2_weight','Stock3_weight','Stock4_weight','mean_return','var_return'))
    print("Mean monthly return for iteration-->",i,"is",pret)
    print("Variance of monthly return for iteration-->",i,"is",pvar)
    print("\n")

# Dataframe containing stock weights,mean and variances of all possible portfolios
print(df)

fig = plt.figure(1, figsize=(20, 10))
plt.scatter(df.mean_return,df.var_return, c=df.var_return)
plt.colorbar()
fig.suptitle('Mean Return VS Volatility', fontsize=20)
plt.xlabel('Volatility', fontsize=18)
plt.ylabel('Mean Return', fontsize=16)
plt.show()