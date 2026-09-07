import numpy as np
import pandas as pd

from finance._validation import aligned, series, window_size
from finance.indicators.trend import ema, sma


def _volume(price: pd.Series, volume: pd.Series) -> tuple[pd.Series, pd.Series]:
    price, volume = aligned(price, volume)
    if (volume < 0).any():
        raise ValueError("volume must be nonnegative")
    return price, volume


def vwma(price: pd.Series, volume: pd.Series, window: int = 20) -> pd.Series:
    price, volume = _volume(price, volume)
    total = volume.rolling(window_size(window)).sum()
    return (price * volume).rolling(window).sum() / total.where(total != 0)


def vwap(price: pd.Series, volume: pd.Series, sessions: pd.Series | None = None) -> pd.Series:
    """Cumulative VWAP; pass exchange-session labels to reset intraday calculations."""
    price, volume = _volume(price, volume)
    if price.isna().any() or volume.isna().any():
        raise ValueError("VWAP requires complete observations")
    flow = price * volume
    if sessions is None:
        return flow.cumsum() / volume.cumsum().replace(0, np.nan)
    if not sessions.index.equals(price.index) or sessions.isna().any():
        raise ValueError("session labels must match the price index")
    return flow.groupby(sessions).cumsum() / volume.groupby(sessions).cumsum().replace(0, np.nan)


def twap(price: pd.Series, window: int = 20) -> pd.Series:
    """TWAP for equally spaced observations; irregular bars must first be resampled."""
    return sma(price, window)


def mfi(
    high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, window: int = 14
) -> pd.Series:
    high, low, close, volume = aligned(high, low, close, volume)
    typical, volume = _volume((high + low + close) / 3, volume)
    direction = typical.diff()
    money = typical * volume
    positive = (
        money.where(direction > 0, 0).mask(direction.isna()).rolling(window_size(window)).sum()
    )
    negative = money.where(direction < 0, 0).mask(direction.isna()).rolling(window).sum()
    total = positive + negative
    return (100 * positive / total.where(total != 0)).mask(total == 0, 50)


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    close, volume = _volume(close, volume)
    return (np.sign(close.diff().fillna(0)) * volume).cumsum()


def pvi(close: pd.Series, volume: pd.Series) -> pd.Series:
    close, volume = _volume(close, volume)
    returns = series(close, positive=True, missing=False).pct_change(fill_method=None).fillna(0)
    return 1000 * (1 + returns.where(volume.diff() > 0, 0)).cumprod()


def pvt(close: pd.Series, volume: pd.Series) -> pd.Series:
    close, volume = _volume(close, volume)
    return (series(close, positive=True).pct_change(fill_method=None).fillna(0) * volume).cumsum()


def accumulation_distribution(
    high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
) -> pd.Series:
    high, low, close, volume = aligned(high, low, close, volume)
    _volume(close, volume)
    width = high - low
    multiplier = ((2 * close - high - low) / width.where(width != 0)).mask(width == 0, 0)
    return (multiplier * volume).cumsum()


def chaikin_money_flow(
    high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, window: int = 20
) -> pd.Series:
    ad = accumulation_distribution(high, low, close, volume)
    flow = ad.diff()
    flow.iloc[0] = ad.iloc[0]
    return flow.rolling(window_size(window)).sum() / volume.rolling(window).sum().replace(0, np.nan)


def chaikin_oscillator(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    fast: int = 3,
    slow: int = 10,
) -> pd.Series:
    if fast >= slow:
        raise ValueError("fast must be smaller than slow")
    ad = accumulation_distribution(high, low, close, volume)
    return ema(ad, fast) - ema(ad, slow)


def force_index(close: pd.Series, volume: pd.Series, window: int = 13) -> pd.Series:
    close, volume = _volume(close, volume)
    return ema(close.diff() * volume, window)


def ease_of_movement(
    high: pd.Series, low: pd.Series, volume: pd.Series, window: int = 14
) -> pd.Series:
    high, low, volume = aligned(high, low, volume)
    _volume(high, volume)
    movement = ((high + low) / 2).diff() * (high - low) / (volume / 1e8).replace(0, np.nan)
    return sma(movement, window)


def balance_of_power(
    open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series
) -> pd.Series:
    open, high, low, close = aligned(open, high, low, close)
    return (close - open) / (high - low).replace(0, np.nan)


def vpci(close: pd.Series, volume: pd.Series, short: int = 5, long: int = 20) -> pd.Series:
    if short >= long:
        raise ValueError("short must be smaller than long")
    confirmation = vwma(close, volume, long) - sma(close, long)
    price_ratio = vwma(close, volume, short) / sma(close, short).replace(0, np.nan)
    volume_ratio = sma(volume, short) / sma(volume, long).replace(0, np.nan)
    return confirmation * price_ratio * volume_ratio
