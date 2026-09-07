import pandas as pd
from _data import load_prices

from finance.analytics import returns, value_at_risk
from finance.data import close_matrix
from finance.portfolio import simulate_portfolio


def main():
    prices = close_matrix(load_prices(("AAPL", "MSFT", "JPM", "SPY")))
    changes = returns(prices).dropna()
    weights = pd.Series(1 / len(prices.columns), index=prices.columns)
    paths = simulate_portfolio(weights, changes.mean() * 252, changes.cov() * 252, seed=12)
    print(paths.iloc[-1].describe().round(2).to_string())
    print(f"Simulated one-year 95% VaR: {value_at_risk(paths.iloc[-1] / 10000 - 1):.2%}")


if __name__ == "__main__":
    main()
