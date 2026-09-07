from numbers import Integral

import numpy as np
import pandas as pd


def window_size(window: int, minimum: int = 1) -> int:
    if isinstance(window, bool) or not isinstance(window, Integral) or window < minimum:
        raise ValueError(f"window must be an integer >= {minimum}")
    return int(window)


def series(values: pd.Series, *, positive: bool = False, missing: bool = True) -> pd.Series:
    if not isinstance(values, pd.Series) or values.empty:
        raise ValueError("expected a nonempty pandas Series")
    if not values.index.is_unique or not values.index.is_monotonic_increasing:
        raise ValueError("index must be unique and increasing")
    result = values.astype(float)
    if np.isinf(result).any() or (not missing and result.isna().any()):
        raise ValueError("values must be finite; missing values are not allowed here")
    if positive and (result.dropna() <= 0).any():
        raise ValueError("prices must be positive")
    return result


def aligned(*values: pd.Series) -> tuple[pd.Series, ...]:
    checked = tuple(series(value) for value in values)
    if any(not checked[0].index.equals(value.index) for value in checked[1:]):
        raise ValueError("series must have identical indexes; align explicitly first")
    return checked


def frame(values: pd.DataFrame, *, positive: bool = False) -> pd.DataFrame:
    if not isinstance(values, pd.DataFrame) or values.empty or not values.columns.is_unique:
        raise ValueError("expected a nonempty DataFrame with unique columns")
    for col in values:
        series(values[col], positive=positive, missing=False)
    return values.astype(float)


def finite(value: float, name: str, *, minimum: float | None = None) -> float:
    value = float(value)
    if not np.isfinite(value) or (minimum is not None and value < minimum):
        raise ValueError(
            f"{name} must be finite" + (f" and >= {minimum}" if minimum is not None else "")
        )
    return value
