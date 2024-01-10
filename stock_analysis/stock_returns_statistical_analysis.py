import yfinance as yf
import datetime as dt
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def analyze_stock_returns(symbol, start, end):
    # Download stock data
    df = yf.download(symbol, start, end)

    # Calculate daily returns
    returns = df['Adj Close'].pct_change().dropna()

    # Calculate and print various statistics
    print('Mean of returns:', np.mean(returns))
    print('Median of returns:', np.median(returns))
    print('Mode of returns:', stats.mode(returns)[0][0])
    print('Arithmetic average of returns:', returns.mean())
    print('Geometric mean of returns:', stats.gmean(returns))
    print('Standard deviation of returns:', returns.std())
    print('Harmonic mean of returns:', len(returns) / np.sum(1.0/returns))
    print('Skewness:', stats.skew(returns))
    print('Kurtosis:', stats.kurtosis(returns))
    
    # Jarque-Bera test
    jarque_bera_results = stats.jarque_bera(returns)
    is_normal = jarque_bera_results[1] > 0.05
    print("Jarque-Bera p-value:", jarque_bera_results[1])
    print('Are the returns normal?', is_normal)

    # Histogram of returns
    plt.hist(returns, bins=30)
    plt.title(f'Histogram of Returns for {symbol.upper()}')
    plt.show()

# Main execution
if __name__ == "__main__":
    symbol = 'AAPL'
    start_date = dt.date.today() - dt.timedelta(days=365*5)
    end_date = dt.date.today()

    analyze_stock_returns(symbol, start_date, end_date)