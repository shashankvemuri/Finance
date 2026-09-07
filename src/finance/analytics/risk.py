from statistics import NormalDist

import numpy as np
import pandas as pd

from finance._validation import finite, series


def value_at_risk(
    values: pd.Series, confidence: float = 0.95, *, method: str = "historical"
) -> float:
    """One-period VaR as a nonnegative loss fraction; no square-root-of-time assumption."""
    values = series(values, missing=False)
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if method == "historical":
        quantile = values.quantile(1 - confidence)
    elif method == "normal":
        if len(values) < 2:
            raise ValueError("normal VaR requires at least two observations")
        quantile = values.mean() + NormalDist().inv_cdf(1 - confidence) * values.std(ddof=1)
    else:
        raise ValueError("method must be historical or normal")
    return float(max(0, -quantile))


def expected_shortfall(values: pd.Series, confidence: float = 0.95) -> float:
    values = series(values, missing=False)
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    tail = values[values <= values.quantile(1 - confidence)]
    return float(max(0, -tail.mean()))


def kelly_fraction(win_probability: float, payoff_ratio: float) -> float:
    """Unconstrained binary-bet Kelly fraction; negative means no long-bet edge."""
    if not 0 <= win_probability <= 1:
        raise ValueError("win_probability must be in [0,1]")
    finite(payoff_ratio, "payoff_ratio", minimum=np.finfo(float).tiny)
    return win_probability - (1 - win_probability) / payoff_ratio


def risk_reward(entry: float, stop: float, target: float, *, short: bool = False) -> float:
    for name, value in [("entry", entry), ("stop", stop), ("target", target)]:
        finite(value, name, minimum=np.finfo(float).tiny)
    risk = stop - entry if short else entry - stop
    reward = entry - target if short else target - entry
    if risk <= 0 or reward <= 0:
        raise ValueError("stop and target must be on opposite, correct sides of entry")
    return reward / risk


def position_size(equity: float, risk_fraction: float, entry: float, stop: float) -> int:
    """Whole shares capped by both loss budget and unlevered purchasing power."""
    finite(equity, "equity", minimum=0)
    finite(entry, "entry", minimum=np.finfo(float).tiny)
    finite(stop, "stop", minimum=np.finfo(float).tiny)
    if not 0 < risk_fraction <= 1 or entry == stop:
        raise ValueError("require 0 < risk_fraction <= 1 and a nonzero stop distance")
    return int(min(equity * risk_fraction / abs(entry - stop), equity / entry))


def return_probability(values: pd.Series, lower: float, upper: float) -> float:
    """Descriptive Gaussian interval probability, not a predictive calibration claim."""
    values = series(values, missing=False)
    if lower >= upper or len(values) < 2 or values.std() == 0:
        raise ValueError("require ordered bounds and nonconstant sample of at least two values")
    normal = NormalDist(values.mean(), values.std())
    return normal.cdf(upper) - normal.cdf(lower)


def net_positioning(long: pd.Series, short: pd.Series, open_interest: pd.Series) -> pd.Series:
    """Net contracts as a fraction of open interest; report dates must not be treated as release dates."""
    from finance._validation import aligned

    long, short, open_interest = aligned(long, short, open_interest)
    if (long < 0).any() or (short < 0).any() or (open_interest <= 0).any():
        raise ValueError("nonnegative positions and positive open interest required")
    return (long - short) / open_interest
