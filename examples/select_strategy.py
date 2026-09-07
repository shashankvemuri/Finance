import pandas as pd
from _data import load_prices

from finance.backtesting import backtest
from finance.strategies import moving_average


def main():
    prices = load_prices()["AAPL"]
    split = int(len(prices) * 0.7)
    candidates = [(10, 50), (20, 50), (20, 100), (50, 200)]
    rows = []
    for fast, slow in candidates:
        signals = moving_average(prices.close.iloc[:split], fast, slow)
        result = backtest(prices.open.iloc[:split], prices.close.iloc[:split], signals)
        rows.append({"fast": fast, "slow": slow, "training_sharpe": result.metrics.sharpe})
    ranking = pd.DataFrame(rows).sort_values("training_sharpe", ascending=False)
    best = ranking.iloc[0]
    signals = moving_average(prices.close, int(best.fast), int(best.slow))
    # Include one flat origin bar to make its closing decision available at the first test open.
    test = prices.iloc[split - 1 :]
    result = backtest(test.open, test.close, signals.iloc[split - 1 :])
    print(ranking.to_string(index=False))
    print("Frozen-parameter chronological holdout:")
    print(result.metrics.round(4).to_string())


if __name__ == "__main__":
    main()
