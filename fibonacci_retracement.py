import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import pandas as pd 
import datetime 

ticker = 'AAPL'
start_date = datetime.datetime(2020,1,1)
end_date = datetime.date.today()

df = DataReader(ticker,'yahoo', start_date, end_date)

# Plot the price series
fig, ax = plt.subplots()
ax.plot(df.Close, color='black')

# Define minimum and maximum price points
price_min = df.Close.min()
price_max = df.Close.max()

# Fibonacci Levels considering original trend as upward move
diff = price_max - price_min
level1 = price_max - 0.236 * diff
level2 = price_max - 0.382 * diff
level3 = price_max - 0.618 * diff

levels = [0, 0.236, 0.382, 0.618, 1]
prices = [price_max, level1, level2, level3, price_min]

dataframe = pd.DataFrame(list(zip(levels, prices)), columns =['Levels', 'Prices']) 

print (dataframe)

ax.axhspan(level1, price_min, alpha=0.4, color='lightsalmon')
ax.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
ax.axhspan(level3, level2, alpha=0.5, color='palegreen')
ax.axhspan(price_max, level3, alpha=0.5, color='powderblue')

plt.ylabel("Price")
plt.xlabel("Date")
plt.legend(loc=2)
plt.show()