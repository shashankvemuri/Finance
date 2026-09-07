from _data import load_prices

from finance.analytics import returns
from finance.data import close_matrix
from finance.portfolio import optimize


def main():
    prices = close_matrix(load_prices(("AAPL", "MSFT", "JPM", "SPY")))
    changes = returns(prices).dropna()
    result = optimize(changes.mean() * 252, changes.cov() * 252, bounds=(0, 0.5))
    print(result.weights.round(4).to_string())
    print(result.statistics.round(4).to_string())


if __name__ == "__main__":
    main()
