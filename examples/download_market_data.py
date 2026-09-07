from finance.data import YahooFinance


def main():
    provider = YahooFinance()
    prices = provider.history("AAPL", "2024-01-01", "2025-01-01")
    print(prices.tail().to_string())
    print(provider.dividends("AAPL", "2024-01-01", "2025-01-01").to_string())


if __name__ == "__main__":
    main()
