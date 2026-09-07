import numpy as np
import pandas as pd

from finance._validation import aligned, series, window_size
from finance.indicators.trend import ema, sma, smma


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder RSI in [0,100]; flat windows are 50; first value follows window changes."""
    changes = series(close).diff()
    up, down = smma(changes.clip(lower=0), window), smma(-changes.clip(upper=0), window)
    total = up + down
    return (100 * up / total.where(total != 0)).mask(total == 0, 50)


def stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 14,
    smooth_k: int = 1,
    smooth_d: int = 3,
) -> pd.DataFrame:
    high, low, close = aligned(high, low, close)
    window_size(window)
    top, bottom = high.rolling(window).max(), low.rolling(window).min()
    width = top - bottom
    raw = (100 * (close - bottom) / width.where(width != 0)).mask(width == 0, 50)
    k = sma(raw, smooth_k)
    return pd.DataFrame({"k": k, "d": sma(k, smooth_d)})


def stochastic_rsi(
    close: pd.Series, window: int = 14, smooth_k: int = 3, smooth_d: int = 3
) -> pd.DataFrame:
    values = rsi(close, window)
    return stochastic(values, values, values, window, smooth_k, smooth_d)


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    return stochastic(high, low, close, window)["k"] - 100


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    if fast >= slow:
        raise ValueError("fast must be smaller than slow")
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": sig, "histogram": line - sig})


def apo(close: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
    return macd(close, fast, slow)["macd"]


def momentum(close: pd.Series, window: int = 10) -> pd.Series:
    return series(close).diff(window_size(window))


def roc(close: pd.Series, window: int = 10) -> pd.Series:
    return series(close, positive=True).pct_change(window_size(window), fill_method=None) * 100


def cci(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
    high, low, close = aligned(high, low, close)
    typical = (high + low + close) / 3
    average = sma(typical, window)
    deviation = typical.rolling(window).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return ((typical - average) / (0.015 * deviation.where(deviation != 0))).mask(deviation == 0, 0)


def dpo(close: pd.Series, window: int = 20) -> pd.Series:
    """Trailing DPO; no centered plotting shift that would expose future data."""
    return series(close).shift(window_size(window) // 2 + 1) - sma(close, window)


def tsi(close: pd.Series, slow: int = 25, fast: int = 13) -> pd.Series:
    changes = series(close).diff()
    denominator = ema(ema(changes.abs(), slow), fast)
    return (100 * ema(ema(changes, slow), fast) / denominator.where(denominator != 0)).mask(
        denominator == 0, 0
    )


def ultimate_oscillator(
    high: pd.Series, low: pd.Series, close: pd.Series, windows: tuple[int, int, int] = (7, 14, 28)
) -> pd.Series:
    high, low, close = aligned(high, low, close)
    if len(windows) != 3 or not windows[0] < windows[1] < windows[2]:
        raise ValueError("provide three increasing windows")
    previous = close.shift()
    bottom = pd.concat([low, previous], axis=1).min(axis=1, skipna=False)
    top = pd.concat([high, previous], axis=1).max(axis=1, skipna=False)
    pressure, span = close - bottom, top - bottom
    values = []
    for window in windows:
        denom = span.rolling(window_size(window)).sum()
        values.append(
            (pressure.rolling(window).sum() / denom.where(denom != 0)).mask(denom == 0, 0.5)
        )
    return 100 * (4 * values[0] + 2 * values[1] + values[2]) / 7


def adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.DataFrame:
    from finance.indicators.volatility import true_range

    high, low, close = aligned(high, low, close)
    up, down = high.diff(), -low.diff()
    plus = up.where((up > down) & (up > 0), 0).mask(up.isna())
    minus = down.where((down > up) & (down > 0), 0).mask(down.isna())
    ranges = true_range(high, low, close).mask(up.isna())
    atr = smma(ranges, window)
    plus_di = (100 * smma(plus, window) / atr.where(atr != 0)).mask(atr == 0, 0)
    minus_di = (100 * smma(minus, window) / atr.where(atr != 0)).mask(atr == 0, 0)
    total = plus_di + minus_di
    dx = (100 * (plus_di - minus_di).abs() / total.where(total != 0)).mask(total == 0, 0)
    return pd.DataFrame({"adx": smma(dx, window), "plus_di": plus_di, "minus_di": minus_di})


def aroon(high: pd.Series, low: pd.Series, window: int = 25) -> pd.DataFrame:
    high, low = aligned(high, low)
    window_size(window)
    up = high.rolling(window + 1).apply(
        lambda x: 100 * (window - np.argmax(x[::-1])) / window, raw=True
    )
    down = low.rolling(window + 1).apply(
        lambda x: 100 * (window - np.argmin(x[::-1])) / window, raw=True
    )
    return pd.DataFrame({"up": up, "down": down, "oscillator": up - down})


def price_momentum_oscillator(
    close: pd.Series, first: int = 35, second: int = 20, signal: int = 10
) -> pd.DataFrame:
    """Double-smoothed ROC variant preserved from the misnamed price_channels script."""
    line = ema(10 * ema(roc(close, 1), first), second)
    return pd.DataFrame({"pmo": line, "signal": ema(line, signal)})


def dynamic_momentum_index(close: pd.Series) -> pd.Series:
    """Experimental volatility-adaptive RSI with trailing 5..30 bar windows."""
    close = series(close)
    vol = close.rolling(5).std()
    ratio = vol / vol.rolling(10).mean()
    windows = (14 / ratio.where(ratio > 0)).clip(5, 30)
    output = pd.Series(np.nan, index=close.index)
    cache = {w: rsi(close, w) for w in range(5, 31)}
    for i, w in enumerate(windows):
        if pd.notna(w):
            output.iloc[i] = cache[int(w)].iloc[i]
    return output
