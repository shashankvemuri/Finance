import numpy as np
import pandas as pd

from finance._validation import aligned, finite, frame, series, window_size
from finance.indicators.trend import ema


def pivot_points(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    *,
    method: str = "classic",
    open: pd.Series | None = None,
) -> pd.DataFrame:
    """Next-bar levels from the previous completed bar; input bars define the pivot period."""
    high, low, close = aligned(high, low, close)
    prior_high, prior_low, prior_close = high.shift(), low.shift(), close.shift()
    pivot, span = (prior_high + prior_low + prior_close) / 3, prior_high - prior_low
    if method == "woodie":
        pivot = (prior_high + prior_low + 2 * prior_close) / 4
    if method == "demark":
        if open is None:
            raise ValueError("DeMark pivots require open prices")
        aligned(close, open)
        prior_open = open.shift()
        x = (prior_high + 2 * prior_low + prior_close).where(
            prior_close < prior_open,
            (2 * prior_high + prior_low + prior_close).where(
                prior_close > prior_open, prior_high + prior_low + 2 * prior_close
            ),
        )
        return pd.DataFrame({"pivot": x / 4, "s1": x / 2 - prior_high, "r1": x / 2 - prior_low})
    result = {"pivot": pivot}
    if method in ("classic", "woodie"):
        result.update(
            r1=2 * pivot - prior_low,
            s1=2 * pivot - prior_high,
            r2=pivot + span,
            s2=pivot - span,
            r3=prior_high + 2 * (pivot - prior_low),
            s3=prior_low - 2 * (prior_high - pivot),
        )
    elif method == "fibonacci":
        for i, ratio in enumerate((0.382, 0.618, 1), 1):
            result[f"r{i}"], result[f"s{i}"] = pivot + ratio * span, pivot - ratio * span
    elif method == "camarilla":
        for i, divisor in enumerate((12, 6, 4, 2), 1):
            result[f"r{i}"], result[f"s{i}"] = (
                prior_close + span * 1.1 / divisor,
                prior_close - span * 1.1 / divisor,
            )
    else:
        raise ValueError("method must be classic, woodie, demark, fibonacci or camarilla")
    bottom = (prior_high + prior_low) / 2
    top = 2 * pivot - bottom
    result.update(cpr_low=np.minimum(top, bottom), cpr_high=np.maximum(top, bottom))
    return pd.DataFrame(result)


def fibonacci_levels(low: float, high: float) -> pd.Series:
    finite(low, "low", minimum=0)
    finite(high, "high", minimum=low)
    ratios = np.array([0, 0.236, 0.382, 0.5, 0.618, 0.786, 1])
    return pd.Series(high - ratios * (high - low), index=ratios, name="level")


def confirmed_extrema(high: pd.Series, low: pd.Series, radius: int = 2) -> pd.DataFrame:
    """Local support/resistance emitted at confirmation, radius bars after the pivot."""
    high, low = aligned(high, low)
    window_size(radius)
    prior_high, prior_low = high.shift(radius), low.shift(radius)
    resistance = prior_high.where(prior_high == high.rolling(2 * radius + 1).max())
    support = prior_low.where(prior_low == low.rolling(2 * radius + 1).min())
    return pd.DataFrame({"support": support, "resistance": resistance})


def green_line(monthly_highs: pd.Series, confirmations: int = 3) -> pd.Series:
    """Record high confirmed by N subsequent lower completed months; supply only closed months."""
    monthly_highs = series(monthly_highs, positive=True, missing=False)
    window_size(confirmations)
    record, confirmed, count = -np.inf, np.nan, 0
    result = []
    for high in monthly_highs:
        if high >= record:
            record, count = high, 0
        else:
            count += 1
            if count == confirmations:
                confirmed = record
        result.append(confirmed)
    return pd.Series(result, index=monthly_highs.index, name="green_line")


def breadth(prices: pd.DataFrame, window: int = 252) -> pd.DataFrame:
    """Counts within an explicitly supplied, complete universe, not the whole exchange."""
    prices = frame(prices, positive=True)
    window_size(window, 2)
    changes = prices.diff()
    advances, declines = (changes > 0).sum(axis=1), (changes < 0).sum(axis=1)
    result = pd.DataFrame(
        {
            "advances": advances,
            "declines": declines,
            "net_advances": advances - declines,
            "new_highs": prices.eq(prices.rolling(window).max()).sum(axis=1),
            "new_lows": prices.eq(prices.rolling(window).min()).sum(axis=1),
        }
    )
    result.loc[result.index[: window - 1], ["new_highs", "new_lows"]] = np.nan
    result.iloc[0, :3] = np.nan
    result["ad_line"] = result.net_advances.cumsum()
    return result


def mcclellan(advances: pd.Series, declines: pd.Series) -> pd.Series:
    advances, declines = aligned(advances, declines)
    if (advances < 0).any() or (declines < 0).any():
        raise ValueError("counts must be nonnegative")
    total = advances + declines
    adjusted = (1000 * (advances - declines) / total.where(total != 0)).mask(total == 0, 0)
    return ema(adjusted, 19) - ema(adjusted, 39)


def arms_index(
    advances: pd.Series,
    declines: pd.Series,
    advancing_volume: pd.Series,
    declining_volume: pd.Series,
) -> pd.Series:
    advances, declines, advancing_volume, declining_volume = aligned(
        advances, declines, advancing_volume, declining_volume
    )
    return (advances / declines.replace(0, np.nan)) / (
        advancing_volume / declining_volume.replace(0, np.nan)
    ).replace(0, np.nan)


def ichimoku(
    high: pd.Series, low: pd.Series, conversion: int = 9, base: int = 26, span: int = 52
) -> pd.DataFrame:
    """Causal conversion/base and unshifted spans; chart projections are not trading inputs."""
    high, low = aligned(high, low)

    def midpoint(w):
        return (high.rolling(window_size(w)).max() + low.rolling(w).min()) / 2

    short, long = midpoint(conversion), midpoint(base)
    return pd.DataFrame(
        {"conversion": short, "base": long, "span_a": (short + long) / 2, "span_b": midpoint(span)}
    )


def gann_fan(
    bars: int,
    anchor_price: float,
    price_per_bar: float,
    ratios: tuple[float, ...] = (0.125, 0.25, 0.5, 1, 2, 4, 8),
) -> pd.DataFrame:
    """Geometric drawing in explicit price/bar units; slopes are not chart-screen angles."""
    window_size(bars)
    finite(anchor_price, "anchor_price", minimum=0)
    finite(price_per_bar, "price_per_bar")
    if not ratios or not np.isfinite(ratios).all() or any(r <= 0 for r in ratios):
        raise ValueError("positive finite slope ratios required")
    steps = np.arange(bars)
    return pd.DataFrame(
        {f"{ratio:g}": anchor_price + price_per_bar * ratio * steps for ratio in ratios},
        index=pd.Index(steps, name="bars_from_anchor"),
    )


def speed_resistance(
    start_price: float, end_price: float, duration: int, bars: int
) -> pd.DataFrame:
    """One-third/two-thirds speed lines from a completed swing, available only at its end."""
    window_size(duration)
    window_size(bars)
    finite(start_price, "start_price", minimum=0)
    finite(end_price, "end_price", minimum=0)
    result = gann_fan(bars, start_price, (end_price - start_price) / duration, (1 / 3, 2 / 3, 1))
    result.iloc[: min(duration, bars)] = np.nan
    return result


def pivot_midpoints(levels: pd.DataFrame) -> pd.DataFrame:
    """Midpoints between adjacent named support/pivot/resistance levels, preserving input timing."""
    if "pivot" not in levels or levels.columns.has_duplicates:
        raise ValueError("provide pivot_points output")
    support = sorted(
        [c for c in levels if c.startswith("s") and c[1:].isdigit()],
        key=lambda c: int(c[1:]),
        reverse=True,
    )
    resistance = sorted(
        [c for c in levels if c.startswith("r") and c[1:].isdigit()], key=lambda c: int(c[1:])
    )
    names = [*support, "pivot", *resistance]
    return pd.DataFrame(
        {
            f"{a}_{b}": (levels[a] + levels[b]) / 2
            for a, b in zip(names[:-1], names[1:], strict=True)
        }
    )
