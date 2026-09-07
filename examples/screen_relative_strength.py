from _data import load_prices

from finance.data import close_matrix
from finance.screening import relative_strength


def main():
    prices = load_prices(("AAPL", "MSFT", "NVDA", "JPM", "SPY"))
    closes = close_matrix(prices)
    print(relative_strength(closes.drop(columns="SPY"), closes.SPY).round(3).to_string())


if __name__ == "__main__":
    main()
