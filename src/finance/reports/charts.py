import numpy as np
import pandas as pd

from finance.data import normalize_ohlcv


def candles(prices: pd.DataFrame, overlays: pd.DataFrame | None = None):
    """Return a matplotlib figure; no display or file writes on calculation."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    prices = normalize_ohlcv(prices)
    if overlays is not None and not overlays.index.equals(prices.index):
        raise ValueError("overlays must align with prices")
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, row in enumerate(prices.itertuples()):
        color = "#16806a" if row.close >= row.open else "#c44848"
        ax.vlines(i, row.low, row.high, color=color, linewidth=1)
        height = abs(row.close - row.open)
        ax.add_patch(
            Rectangle(
                (i - 0.3, min(row.open, row.close)), 0.6, height or row.close * 0.00001, color=color
            )
        )
    if overlays is not None:
        for column in overlays:
            ax.plot(range(len(prices)), overlays[column], label=column, linewidth=1)
        ax.legend()
    ticks = np.linspace(0, len(prices) - 1, min(6, len(prices)), dtype=int)
    ax.set_xticks(ticks, prices.index[ticks].strftime("%Y-%m-%d"))
    ax.set_ylabel("Price")
    ax.autoscale_view()
    fig.tight_layout()
    return fig


def correlation_heatmap(correlation: pd.DataFrame):
    import matplotlib.pyplot as plt

    if (
        not correlation.index.equals(pd.Index(correlation.columns))
        or not np.isfinite(correlation).all().all()
    ):
        raise ValueError("finite square matrix with matching labels required")
    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(correlation, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(correlation)), correlation.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(correlation)), correlation.index)
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    return fig


def equity_chart(result):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    result.equity.plot(ax=ax, label="Strategy")
    result.benchmark.plot(ax=ax, label="Buy and hold")
    ax.set_ylabel("Account value")
    ax.legend()
    fig.tight_layout()
    return fig
