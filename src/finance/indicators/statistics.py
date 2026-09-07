import numpy as np
import pandas as pd

from finance._validation import aligned, series, window_size


def zscore(values: pd.Series, window: int = 20) -> pd.Series:
    values = series(values)
    deviation = values.rolling(window_size(window, 2)).std(ddof=0)
    return ((values - values.rolling(window).mean()) / deviation.where(deviation != 0)).mask(
        deviation == 0, 0
    )


def covariance(x: pd.Series, y: pd.Series, window: int = 20) -> pd.Series:
    x, y = aligned(x, y)
    return x.rolling(window_size(window, 2)).cov(y)


def correlation(x: pd.Series, y: pd.Series, window: int = 20) -> pd.Series:
    x, y = aligned(x, y)
    return x.rolling(window_size(window, 2)).corr(y)


def beta(asset_returns: pd.Series, market_returns: pd.Series, window: int = 60) -> pd.Series:
    return covariance(asset_returns, market_returns, window) / market_returns.rolling(
        window
    ).var().replace(0, np.nan)


def relative_price(close: pd.Series, benchmark: pd.Series) -> pd.Series:
    close, benchmark = aligned(close, benchmark)
    return close / benchmark.replace(0, np.nan)


def rolling_regression(values: pd.Series, window: int = 20) -> pd.DataFrame:
    """Trailing OLS against bar number; slope is price units per bar, not a forecast."""
    values = series(values)
    window_size(window, 2)
    x = np.arange(window, dtype=float)
    centered = x - x.mean()
    slope = values.rolling(window).apply(lambda y: centered @ y / (centered @ centered), raw=True)
    intercept = values.rolling(window).mean() - slope * x.mean()
    return pd.DataFrame(
        {"slope": slope, "intercept": intercept, "fitted": intercept + slope * (window - 1)}
    )


def geometric_return(close: pd.Series, window: int = 20) -> pd.Series:
    """Geometric mean per-bar return over window price changes, as a fraction."""
    close = series(close, positive=True)
    window_size(window)
    return (close / close.shift(window)) ** (1 / window) - 1
