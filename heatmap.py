import numpy as np 
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import datetime as datetime
from matplotlib.colors import ListedColormap

pd.set_option('display.max_columns', None)

start_date = datetime.datetime.now() - datetime.timedelta(days=3)
end_date = datetime.date.today() 
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'WMT', 'COST', 'NFLX', 'TSLA', 'SBUX', 'TGT', 'GM', 'GE', 'NIO', 'NKE', 'AXP']

df = DataReader(stocks, 'yahoo', start_date, end_date)['Close']

df = df.reset_index()
df = df.drop(['Date'], axis=1)

dataframe = df.pct_change()
dataframe.index = ['Nothing', 'Change']
dataframe = dataframe.drop(['Nothing'])
dataframe = dataframe.transpose()
print (dataframe)

dataframe = dataframe.reset_index()

Yrows = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4]
Xcols = [1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4]

dataframe['Yrows'] = Yrows
dataframe['Xcols'] = Xcols

print (dataframe)

dataframe = dataframe.sort_values('Change', ascending=False)

symbol = ((np.asarray(dataframe['Symbols'])).reshape(4, 4))
perchange = ((np.asarray(dataframe['Change'])).reshape(4, 4))

print (symbol)
print (perchange)

result = dataframe.pivot(index='Yrows', columns='Xcols', values = 'Change')
print (result)

labels = (np.asarray(["{0} \n {1:.2f}".format(symb, value)
                      for symb, value in zip(symbol.flatten(), 
                                             perchange.flatten())])
          ).reshape(4,4)


fig, ax = plt.subplots(figsize=(12,7))

title = "Heat Map"

plt.title(title, fontsize=18)
ttl = ax.title
ttl.set_position([0.5, 1.05])
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

sns.heatmap(result, annot=labels, fmt="", vmin=-0.2, cmap='YlOrRd', linewidths=0.30, ax=ax)
plt.show()
