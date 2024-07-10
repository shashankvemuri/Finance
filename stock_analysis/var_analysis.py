import yfinance as yf
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def calculate_var(stock, start, end):
    # Download data from Yahoo Finance
    df = yf.download(stock, start, end)
    
    # Calculate daily returns
    returns = df['Adj Close'].pct_change().dropna()

    # VaR using historical bootstrap method
    plt.figure(figsize=(10, 5))
    returns.hist(bins=40, density=True, histtype='stepfilled', alpha=0.5)
    plt.title("Histogram of stock daily returns")
    plt.show()

    # VaR using variance-covariance method
    tdf, tmean, tsigma = stats.t.fit(returns)
    support = np.linspace(returns.min(), returns.max(), 100)
    plt.figure(figsize=(10, 5))
    plt.plot(support, stats.t.pdf(support, loc=tmean, scale=tsigma, df=tdf), "r-")
    plt.title("VaR using variance-covariance method")
    plt.show()

    # Calculate VaR using normal distribution at 95% confidence level
    mean, sigma = returns.mean(), returns.std()
    VaR = stats.norm.ppf(0.05, mean, sigma)
    print("VaR using normal distribution at 95% confidence level:", VaR)

# Main execution
if __name__ == "__main__":
    stock = "AMD"
    start = dt.date.today() - dt.timedelta(days=365*9)
    end = dt.date.today()
    calculate_var(stock, start, end)