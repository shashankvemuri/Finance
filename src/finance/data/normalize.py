import re

import numpy as np
import pandas as pd


def normalize_ticker(ticker: str) -> str:
    """Normalize Yahoo share-class symbols (BRK.B -> BRK-B); retain index/FX suffixes."""
    ticker = ticker.strip().upper().replace(".", "-")
    if not re.fullmatch(r"[A-Z0-9^][A-Z0-9^=\-]{0,24}", ticker):
        raise ValueError(f"invalid ticker: {ticker!r}")
    return ticker


def normalize_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate one ticker's OHLCV. Never fill gaps or mix adjusted and raw prices."""
    if not isinstance(raw, pd.DataFrame) or raw.empty:
        raise ValueError("provider returned no price rows")
    data = raw.copy()
    if isinstance(data.columns, pd.MultiIndex):
        singleton = [
            i
            for i in range(data.columns.nlevels)
            if len(data.columns.get_level_values(i).unique()) == 1
        ]
        if len(singleton) != 1:
            raise ValueError("expected exactly one ticker")
        data.columns = data.columns.droplevel(singleton[0])
    data.columns = [str(c).strip().lower().replace(" ", "_") for c in data.columns]
    if not data.columns.is_unique:
        raise ValueError("duplicate columns")
    if "date" in data:
        data = data.set_index("date")
    if not isinstance(data.index, pd.DatetimeIndex):
        if pd.api.types.is_numeric_dtype(data.index):
            raise ValueError("price index must contain dates")
        data.index = pd.to_datetime(data.index, errors="raise")
    if data.index.hasnans or not data.index.is_unique:
        raise ValueError("missing or duplicate timestamps")
    data = data.sort_index()
    required = ["open", "high", "low", "close", "volume"]
    if missing := set(required) - set(data.columns):
        raise ValueError(f"missing OHLCV columns: {sorted(missing)}")
    data = data[required].apply(pd.to_numeric, errors="raise").astype(float)
    if not np.isfinite(data.to_numpy()).all():
        raise ValueError("OHLCV contains missing or nonfinite values")
    if (data[["open", "high", "low", "close"]] <= 0).any().any() or (data.volume < 0).any():
        raise ValueError("prices must be positive and volume nonnegative")
    tolerance = data.high * 1e-8
    if (
        (data.high + tolerance < data[["open", "low", "close"]].max(axis=1))
        | (data.low - tolerance > data[["open", "high", "close"]].min(axis=1))
    ).any():
        raise ValueError("inconsistent OHLC bounds; check adjustment basis")
    data.index.name = "date"
    return data
