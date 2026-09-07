import numpy as np
import pandas as pd

from finance._validation import aligned, finite, series, window_size
from finance.indicators.trend import ema, sma, smma


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    high, low, close = aligned(high, low, close)
    result = pd.concat(
        [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1
    ).max(axis=1)
    return result.mask(high.isna() | low.isna() | close.isna())


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder ATR, seeded by window ranges (first range is high-low)."""
    return smma(true_range(high, low, close), window)


def realized_volatility(close: pd.Series, window: int = 20, periods: int = 252) -> pd.Series:
    return series(close, positive=True).pct_change(fill_method=None).rolling(
        window_size(window, 2)
    ).std() * np.sqrt(window_size(periods))


def variance(values: pd.Series, window: int = 20) -> pd.Series:
    return series(values).rolling(window_size(window, 2)).var(ddof=1)


def standard_deviation(values: pd.Series, window: int = 20) -> pd.Series:
    return np.sqrt(variance(values, window))


def bollinger_bands(close: pd.Series, window: int = 20, deviations: float = 2) -> pd.DataFrame:
    """Population standard deviation (ddof=0); bandwidth is a fraction of the middle."""
    middle = sma(close, window)
    spread = series(close).rolling(window).std(ddof=0) * finite(deviations, "deviations", minimum=0)
    return pd.DataFrame(
        {
            "lower": middle - spread,
            "middle": middle,
            "upper": middle + spread,
            "bandwidth": 2 * spread / middle.where(middle != 0),
        }
    )


def envelopes(close: pd.Series, window: int = 20, fraction: float = 0.025) -> pd.DataFrame:
    middle = sma(close, window)
    finite(fraction, "fraction", minimum=0)
    return pd.DataFrame(
        {"lower": middle * (1 - fraction), "middle": middle, "upper": middle * (1 + fraction)}
    )


def donchian(high: pd.Series, low: pd.Series, window: int = 20) -> pd.DataFrame:
    high, low = aligned(high, low)
    window_size(window)
    upper, lower = high.rolling(window).max(), low.rolling(window).min()
    return pd.DataFrame({"lower": lower, "middle": (upper + lower) / 2, "upper": upper})


def keltner(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 20,
    atr_window: int = 10,
    multiplier: float = 2,
) -> pd.DataFrame:
    middle = ema(close, window)
    spread = atr(high, low, close, atr_window) * finite(multiplier, "multiplier", minimum=0)
    return pd.DataFrame({"lower": middle - spread, "middle": middle, "upper": middle + spread})


def acceleration_bands(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20
) -> pd.DataFrame:
    high, low, close = aligned(high, low, close)
    factor = 4 * (high - low) / (high + low).replace(0, np.nan)
    return pd.DataFrame(
        {
            "lower": sma(low * (1 - factor), window),
            "middle": sma(close, window),
            "upper": sma(high * (1 + factor), window),
        }
    )


def relative_volatility_index(close: pd.Series, window: int = 14) -> pd.Series:
    """Directional standard-deviation ratio, Wilder-smoothed, in [0,100]."""
    close = series(close)
    deviation = standard_deviation(close, window)
    up = smma(deviation.where(close.diff() > 0, 0).mask(deviation.isna()), window)
    down = smma(deviation.where(close.diff() < 0, 0).mask(deviation.isna()), window)
    total = up + down
    return (100 * up / total.where(total != 0)).mask(total == 0, 50)


def supertrend(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 10, multiplier: float = 3
) -> pd.DataFrame:
    high, low, close = aligned(high, low, close)
    if any(s.isna().any() for s in (high, low, close)):
        raise ValueError("supertrend requires complete OHLC")
    spread = atr(high, low, close, window) * finite(multiplier, "multiplier", minimum=0)
    upper = ((high + low) / 2 + spread).to_numpy(copy=True)
    lower = ((high + low) / 2 - spread).to_numpy(copy=True)
    prices = close.to_numpy()
    line, direction = np.full(len(close), np.nan), np.full(len(close), np.nan)
    for i in range(window - 1, len(close)):
        if i == window - 1:
            direction[i], line[i] = -1, upper[i]
            continue
        if prices[i - 1] <= upper[i - 1]:
            upper[i] = min(upper[i], upper[i - 1])
        if prices[i - 1] >= lower[i - 1]:
            lower[i] = max(lower[i], lower[i - 1])
        if direction[i - 1] == -1:
            direction[i] = 1 if prices[i] > upper[i] else -1
        else:
            direction[i] = -1 if prices[i] < lower[i] else 1
        line[i] = lower[i] if direction[i] == 1 else upper[i]
    return pd.DataFrame({"supertrend": line, "direction": direction}, index=close.index)
