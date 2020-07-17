import matplotlib.pyplot as plt
import san

data = san.get("ohlcv/bitcoin", from_date="2017-01-01")

data["MA_50"] = data.closePriceUsd.rolling(50).mean()
data["MA_100"] = data.closePriceUsd.rolling(100).mean()
data["returns"] = data.closePriceUsd.pct_change()


trades = data.MA_50 > data.MA_100  # defining the strategy

strategy_perf = (data.returns.shift(-1) * trades + 1).cumprod()  # backtesting

holding_perf = (data.returns.shift(-1) + 1).cumprod()  # benchmark


plt.style.use("fivethirtyeight")
plt.figure(figsize=(20,10))
plt.title("Simple Backtest Example")
plt.ylabel("multiple of the returns")
plt.plot(strategy_perf, label="strategy")
plt.plot(holding_perf, label="holding")
plt.legend()
plt.show()