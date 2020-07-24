import numpy
import scipy.stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import datetime as dt

stock = "AMD"
start = dt.date.today() - dt.timedelta(days = 365*9)
end = dt.date.today()
df = pdr.get_data_yahoo(stock, start, end)

plt.figure(figsize=(15,8))
df["Adj Close"].plot()
plt.title(f"{stock} Adj Close", weight='bold')
plt.show()

plt.gcf()
fig = plt.figure()
fig.set_size_inches(10,3)
df["Adj Close"].pct_change().plot()
plt.title(u"{} daily returns".format(stock), weight='bold')
plt.show()

plt.gcf()
df["Adj Close"].pct_change().hist(bins=50, density=True, histtype='stepfilled', alpha=0.5)
plt.title(u"Histogram of stock daily returns", weight='bold')
df["Adj Close"].pct_change().std()
plt.show()

Q = df["Adj Close"].pct_change().dropna().tolist()
plt.gcf()
scipy.stats.probplot(Q, dist=scipy.stats.norm, plot=plt.figure().add_subplot(111))
plt.title("Normal QQ-plot of daily returns", weight="bold");
plt.show()

tdf, tmean, tsigma = scipy.stats.t.fit(Q)
plt.gcf()
scipy.stats.probplot(Q, dist=scipy.stats.t, sparams=(tdf, tmean, tsigma), plot=plt.figure().add_subplot(111))
plt.title("Student QQ-plot of Stock daily returns", weight="bold");
plt.show()

# VaR using the historical bootstrap method
returns = df["Adj Close"].pct_change().dropna()
mean = returns.mean()
sigma = returns.std()
plt.gcf()
tdf, tmean, tsigma = scipy.stats.t.fit(returns.tolist())
returns.hist(bins=40, density=True, histtype='stepfilled', alpha=0.5);
plt.show()

# VaR using the variance-covariance method
support = numpy.linspace(returns.min(), returns.max(), 100)
plt.gcf()
returns.hist(bins=40, density=True, histtype='stepfilled', alpha=0.5);
plt.plot(support, scipy.stats.t.pdf(support, loc=tmean, scale=tsigma, df=tdf), "r-")
plt.title("Daily change in HAL (%)", weight='bold')
plt.show()

print(scipy.stats.norm.ppf(0.05, mean, sigma))
# VaR using Monte Carlo method
days = 300   # time horizon
dt = 1/float(days)
sigma = 0.04 # volatility
mu = 0.05  # drift (average growth rate)

def random_walk(startprice):
    price = numpy.zeros(days)
    shock = numpy.zeros(days)
    price[0] = startprice
    for i in range(1, days):
        shock[i] = numpy.random.normal(loc=mu * dt, scale=sigma * numpy.sqrt(dt))
        price[i] = max(0, price[i-1] + shock[i] * price[i-1])
    return price

# Similuations
plt.gcf()
for run in range(30):
    plt.plot(random_walk(10.0))
plt.xlabel("Time")
plt.ylabel("Price");
plt.show()

runs = 10000
simulations = numpy.zeros(runs)
for run in range(runs):
    simulations[run] = random_walk(10.0)[days-1]
q = numpy.percentile(simulations, 1)
plt.gcf()
plt.hist(simulations, density=True, bins=30, histtype='stepfilled', alpha=0.5)
plt.figtext(0.6, 0.8, "Start price: %.2f" % df["Adj Close"][0])
plt.figtext(0.6, 0.7, "Mean final price: %.2f" % simulations.mean())
plt.figtext(0.6, 0.6, "VaR(0.99): %.2f" % (10 - q,))
plt.figtext(0.15, 0.6, "q(0.99): %.2f" % q)
plt.axvline(x=q, linewidth=4, color='r')
plt.title("Final price distribution after {} days".format(days), weight='bold');
plt.show()