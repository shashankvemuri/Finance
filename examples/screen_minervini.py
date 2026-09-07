from _data import load_prices

from finance.screening import minervini


def main():
    prices = load_prices(("AAPL", "MSFT", "NVDA", "JPM", "SPY"))
    benchmark = prices.pop("SPY").close
    print(minervini(prices, benchmark).round(3).to_string())


if __name__ == "__main__":
    main()
