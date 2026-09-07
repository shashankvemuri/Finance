from _data import load_prices

from finance.indicators import bollinger_bands, rsi


def main():
    import matplotlib.pyplot as plt

    prices = load_prices()["AAPL"].tail(200)
    bands = bollinger_bands(prices.close)
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10, 6), height_ratios=[2, 1])
    prices.close.plot(ax=axes[0], label="Close")
    axes[0].fill_between(prices.index, bands.lower, bands.upper, alpha=0.2)
    rsi(prices.close).plot(ax=axes[1], label="RSI")
    axes[1].set_ylim(0, 100)
    for axis in axes:
        axis.legend()
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
