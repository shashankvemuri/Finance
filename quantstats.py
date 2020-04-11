import quantstats as qs

# extend pandas functionality with metrics, etc.
qs.extend_pandas()

# fetch the daily returns for a stock
stock = qs.utils.download_returns('FB')

# show sharpe ratio
qs.stats.sharpe(stock)

# or using extend_pandas() :)
print (stock.sharpe())

qs.plots.snapshot(stock, title='Facebook Performance')

stock.plot_snapshot(title='Facebook Performance')

qs.reports.html(stock, "SPY")

print([f for f in dir(qs.stats) if f[0] != '_'])