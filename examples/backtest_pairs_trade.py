import pandas as pd
from _data import load_prices

from finance.backtesting import backtest
from finance.strategies import pairs_trade


def main():
    prices = load_prices(("JPM", "BAC"))
    closes = pd.DataFrame({k: v.close for k, v in prices.items()})
    opens = pd.DataFrame({k: v.open for k, v in prices.items()})
    targets = pairs_trade(closes.JPM, closes.BAC).set_axis(closes.columns, axis=1)
    result = backtest(opens, closes, targets, commission=0.001, borrow_rate=0.03)
    print("Experimental log-ratio strategy; this pair has not been selected for cointegration.")
    print(result.metrics.round(4).to_string())
    print(result.trades.tail().to_string(index=False))


if __name__ == "__main__":
    main()
