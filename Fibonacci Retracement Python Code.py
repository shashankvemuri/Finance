# To plot
import matplotlib.pyplot as plt

# To import stock prices
import fix_yahoo_finance as yf  
df = yf.download('XOM','2017-08-01', '2017-12-31')

# Plot the price series
fig, ax = plt.subplots()
ax.plot(df.Close, color='black')

# Define minimum and maximum price points
price_min = 76 #df.Close.min()
price_max = 84 #df.Close.max()

# Fibonacci Levels considering original trend as upward move
diff = price_max - price_min
level1 = price_max - 0.236 * diff
level2 = price_max - 0.382 * diff
level3 = price_max - 0.618 * diff

print "Level", "Price"
print "0 ", price_max
print "0.236", level1
print "0.382", level2
print "0.618", level3
print "1 ", price_min

ax.axhspan(level1, price_min, alpha=0.4, color='lightsalmon')
ax.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
ax.axhspan(level3, level2, alpha=0.5, color='palegreen')
ax.axhspan(price_max, level3, alpha=0.5, color='powderblue')

plt.ylabel("Price")
plt.xlabel("Date")
plt.legend(loc=2)
plt.show()
