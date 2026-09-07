import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from finance.data import normalize_ohlcv, normalize_ticker
from finance.screening import (
    dividend_screen,
    fundamental_screen,
    ibd_relative_strength,
    minervini,
    relative_strength,
    rsi_screen,
)


def test_normalize(ohlcv):
    original = ohlcv.copy()
    raw = ohlcv.rename(columns=str.title).iloc[::-1]
    actual = normalize_ohlcv(raw)
    assert actual.index.is_monotonic_increasing
    assert list(actual) == ["open", "high", "low", "close", "volume"]
    pd.testing.assert_frame_equal(original, ohlcv)
    raw.columns = pd.MultiIndex.from_product([raw.columns, ["AAPL"]])
    assert_allclose(normalize_ohlcv(raw), actual)
    assert normalize_ticker(" brk.b ") == "BRK-B"
    with pytest.raises(ValueError):
        normalize_ticker("a/b")
    with pytest.raises(ValueError):
        normalize_ohlcv(ohlcv.assign(high=1))
    with pytest.raises(ValueError):
        normalize_ohlcv(ohlcv.iloc[[0, 0]])
    with pytest.raises(ValueError):
        normalize_ohlcv(ohlcv.assign(volume=-1))
    with pytest.raises(ValueError):
        normalize_ohlcv(ohlcv.reset_index(drop=True))
    with pytest.raises(ValueError):
        normalize_ohlcv(ohlcv.assign(close=np.nan))


def test_screens_hand_constructed_trends():
    index = pd.bdate_range("2020-01-01", periods=300)
    close = pd.DataFrame(
        {
            "fast": 100 * np.exp(np.arange(300) * 0.003),
            "slow": 100 * np.exp(np.arange(300) * 0.001),
        },
        index=index,
    )
    benchmark = pd.Series(100 * np.exp(np.arange(300) * 0.002), index=index)
    ranks = relative_strength(close, benchmark)
    assert ranks.loc["fast", "rank"] == 100
    assert ranks.loc["slow", "rank"] == 50
    assert ranks.loc["fast", "relative_strength"] == pytest.approx(np.exp(0.001 * 252))
    ibd = ibd_relative_strength(close)
    expected = sum(
        w * (np.exp(0.003 * n) - 1)
        for w, n in zip([0.4, 0.2, 0.2, 0.2], [63, 126, 189, 252], strict=True)
    )
    assert ibd.loc["fast", "score"] == pytest.approx(expected)
    bars = {
        ticker: pd.DataFrame(
            {
                "open": close[ticker],
                "high": close[ticker] * 1.01,
                "low": close[ticker] * 0.99,
                "close": close[ticker],
                "volume": 1000.0,
            }
        )
        for ticker in close
    }
    screen = minervini(bars, benchmark)
    assert bool(screen.loc["fast", "passed"])
    assert not bool(screen.loc["slow", "passed"])
    assert_allclose(rsi_screen(close).rsi, 100)
    with pytest.raises(ValueError):
        relative_strength(close.iloc[:100], benchmark.iloc[:100])


def test_fundamental_fractional_units():
    companies = pd.DataFrame(
        {
            "roe": [0.2, 0.01, np.nan],
            "revenue_growth": [0.2, 0.2, 0.2],
            "earnings_growth": [0.2, 0.2, 0.2],
            "pe": [20, 20, 20],
            "dividend_yield": [0.03, 0.01, 0.04],
        }
    )
    assert fundamental_screen(companies).passed.tolist() == [True, False, False]
    screened = dividend_screen(companies).sort_index()
    assert screened.passed.tolist() == [True, False, True]
