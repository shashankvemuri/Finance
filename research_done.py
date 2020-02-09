
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
from scipy.stats.mstats import mquantiles

pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_colwidth', 1000)
pd.set_option('display.width', 100)

#BASEPATH = '/home/steve/GDrive/Shashank_Proj/'


df = pd.read_csv(r"C:\Users\Sagar\Downloads\djia - djia.csv")
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# Print out stock data
print(df.tail())


# compute returns 

rtndf = df.pct_change()

print(rtndf)


# Daily volatility of stocks:
print(rtndf['2011':'2015'].std())


# Quantiles after date filtering. 
qtiledf = rtndf['2011':'2015'].apply(lambda x:mquantiles(x,[0.01,0.05,0.95,0.99])).transpose()
print(qtiledf)
plt.plot(qtiledf)


# Rolling operations 
tstst = 'AAPL'
stkdf = rtndf[tstst] 

stkdf.loc[np.abs(stkdf) > 0.49 ] = 0

rollvol = rtndf[tstst].dropna().rolling(252).std().dropna()

# hist plot
stksplot = ['AAPL','NKE','IBM','MRK','CSCO','PG','AXP','CAT','MSFT','GS', 'PFE', 'JPM']

rtndf[stksplot].hist(bins=300)
plt.show()
