import quantstats as qs
import matplotlib.pyplot as plt

# extend pandas functionality with metrics, etc.
qs.extend_pandas()

# fetch the daily returns for a stock
stock = qs.utils.download_returns('AAPL')

qs.reports.html(stock, "SPY")
plt.show()