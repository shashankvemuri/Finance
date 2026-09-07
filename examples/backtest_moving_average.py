from _data import load_prices

from finance.backtesting import backtest
from finance.strategies import moving_average


def main():
    prices = load_prices()["AAPL"]
    targets = moving_average(prices.close, fast=20, slow=50)
    result = backtest(prices.open, prices.close, targets, commission=0.001)
    print(result.metrics.round(4).to_string())
    print(result.trades.tail().to_string(index=False))


if __name__ == "__main__":
    main()
