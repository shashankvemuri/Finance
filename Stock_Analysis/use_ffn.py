import ffn
import matplotlib.pyplot as plt
import matplotlib

prices = ffn.get('aapl,msft', start='2020-04-01')
stats = prices.calc_stats()
print(stats.display())