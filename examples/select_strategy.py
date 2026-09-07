from functools import partial

from _data import load_prices

from finance.strategies import moving_average, select_strategy


def signal(prices, fast, slow):
    return moving_average(prices.close, fast, slow)


def main():
    prices = load_prices()["AAPL"]
    candidates = {
        f"SMA {fast}/{slow}": partial(signal, fast=fast, slow=slow)
        for fast, slow in [(10, 50), (20, 50), (20, 100), (50, 200)]
    }
    selection = select_strategy(prices, candidates, metric="sharpe")
    print(selection.training_scores[["candidate", "sharpe"]].to_string(index=False))
    print("Selected:", selection.selected)
    print("Chronological holdout:")
    print(selection.holdout.metrics.round(4).to_string())


if __name__ == "__main__":
    main()
