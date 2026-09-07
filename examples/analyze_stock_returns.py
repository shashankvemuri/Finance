from _data import load_prices

from finance.analytics import capm, performance, returns, value_at_risk
from finance.data import close_matrix


def main():
    prices = close_matrix(load_prices(("AAPL", "SPY")))
    changes = returns(prices).dropna()
    print(performance(changes.AAPL).round(4).to_string())
    print(capm(changes.AAPL, changes.SPY).round(4).to_string())
    print(f"Historical daily 95% VaR: {value_at_risk(changes.AAPL):.2%}")


if __name__ == "__main__":
    main()
