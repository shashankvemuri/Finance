"""Shared example inputs: deterministic synthetic bars, or explicit --live Yahoo data."""

import hashlib
import sys

import numpy as np
import pandas as pd

from finance.data import YahooFinance


def load_prices(tickers=("AAPL",), *, start="2022-01-01", end="2025-01-01"):
    if "--live" in sys.argv:
        provider = YahooFinance()
        return {ticker: provider.history(ticker, start, end) for ticker in tickers}
    index = pd.bdate_range("2022-01-03", periods=750)
    market = np.random.default_rng(42).normal(0.0003, 0.009, len(index))
    result = {}
    for ticker in tickers:
        seed = int.from_bytes(hashlib.sha256(ticker.encode()).digest()[:4], "big")
        rng = np.random.default_rng(seed)
        close = 100 * np.exp(np.cumsum(market + rng.normal(0.0002, 0.005, len(index))))
        opening = close * np.exp(rng.normal(0, 0.002, len(index)))
        result[ticker] = pd.DataFrame(
            {
                "open": opening,
                "high": np.maximum(opening, close) * 1.01,
                "low": np.minimum(opening, close) * 0.99,
                "close": close,
                "volume": rng.integers(100000, 1000000, len(index)).astype(float),
            },
            index=index,
        )
    return result
