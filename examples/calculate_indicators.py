from _data import load_prices

from finance.indicators import atr, bollinger_bands, macd, rsi


def main():
    prices = load_prices()["AAPL"]
    result = prices[["close"]].assign(
        rsi=rsi(prices.close), atr=atr(prices.high, prices.low, prices.close)
    )
    result = result.join(bollinger_bands(prices.close)).join(macd(prices.close))
    print(result.tail().round(3).to_string())


if __name__ == "__main__":
    main()
