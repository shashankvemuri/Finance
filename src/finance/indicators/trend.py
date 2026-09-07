import numpy as np
import pandas as pd

from finance._validation import series, window_size


def sma(close: pd.Series, window: int = 20) -> pd.Series:
    return series(close).rolling(window_size(window)).mean()


def ema(close: pd.Series, window: int = 20) -> pd.Series:
    """Recursive EMA, seeded with the first observation; window-1 warm-up rows."""
    return series(close).ewm(span=window_size(window), adjust=False, min_periods=window).mean()


def ewma(close: pd.Series, window: int = 20) -> pd.Series:
    return ema(close, window)


def wma(close: pd.Series, window: int = 20) -> pd.Series:
    window_size(window)
    weights = np.arange(1, window + 1, dtype=float)
    return series(close).rolling(window).apply(lambda x: x @ weights / weights.sum(), raw=True)


def smma(close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder smoothing: seed with a full SMA, reset after a missing observation."""
    close = series(close)
    window_size(window)
    values = close.to_numpy()
    output = np.full(len(values), np.nan)
    count = 0
    previous = np.nan
    for i, value in enumerate(values):
        if np.isnan(value):
            count, previous = 0, np.nan
            continue
        count += 1
        if count == window:
            previous = values[i - window + 1 : i + 1].mean()
        elif count > window:
            previous += (value - previous) / window
        output[i] = previous
    return pd.Series(output, index=close.index, name=close.name)


def dema(close: pd.Series, window: int = 20) -> pd.Series:
    first = ema(close, window)
    return 2 * first - ema(first, window)


def tema(close: pd.Series, window: int = 20) -> pd.Series:
    first = ema(close, window)
    second = ema(first, window)
    return 3 * first - 3 * second + ema(second, window)


def trima(close: pd.Series, window: int = 20) -> pd.Series:
    window_size(window)
    return sma(sma(close, (window + 1) // 2), window // 2 + 1)


def hma(close: pd.Series, window: int = 20) -> pd.Series:
    window_size(window, 2)
    return wma(2 * wma(close, window // 2) - wma(close, window), int(np.sqrt(window)))


def ribbon(
    close: pd.Series,
    windows: tuple[int, ...] = (3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60),
    *,
    exponential: bool = True,
) -> pd.DataFrame:
    """GMMA defaults; supply other windows for a moving-average ribbon."""
    if not windows or len(set(windows)) != len(windows):
        raise ValueError("provide unique windows")
    average = ema if exponential else sma
    return pd.DataFrame({str(w): average(close, w) for w in windows})
