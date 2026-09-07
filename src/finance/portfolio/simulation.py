import numpy as np
import pandas as pd

from finance._validation import finite, series, window_size
from finance.portfolio.allocation import _inputs, _weights


def geometric_brownian_motion(
    initial: float,
    drift: float,
    volatility: float,
    *,
    years: float = 1,
    steps: int = 252,
    paths: int = 1000,
    seed: int = 0,
) -> pd.DataFrame:
    """GBM with annual arithmetic drift and volatility, including initial value at t=0."""
    finite(initial, "initial", minimum=np.finfo(float).tiny)
    finite(drift, "drift")
    finite(volatility, "volatility", minimum=0)
    finite(years, "years", minimum=np.finfo(float).tiny)
    window_size(steps)
    window_size(paths)
    dt = years / steps
    shocks = np.random.default_rng(seed).standard_normal((steps, paths))
    changes = (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * shocks
    values = initial * np.exp(np.vstack([np.zeros(paths), np.cumsum(changes, axis=0)]))
    return pd.DataFrame(values, index=pd.Index(np.linspace(0, years, steps + 1), name="years"))


def simulate_portfolio(
    weights: pd.Series,
    mean: pd.Series,
    covariance: pd.DataFrame,
    *,
    initial: float = 10000,
    years: float = 1,
    steps: int = 252,
    paths: int = 1000,
    seed: int = 0,
) -> pd.DataFrame:
    """Correlated GBM assets with fixed-share buy-and-hold weights; annual inputs."""
    mean, covariance = _inputs(mean, covariance)
    weights = _weights(weights, mean.index)
    finite(initial, "initial", minimum=np.finfo(float).tiny)
    finite(years, "years", minimum=np.finfo(float).tiny)
    window_size(steps)
    window_size(paths)
    values, vectors = np.linalg.eigh(covariance)
    root = vectors @ np.diag(np.sqrt(np.maximum(values, 0)))
    dt = years / steps
    rng = np.random.default_rng(seed)
    asset_values = np.ones((paths, len(mean)))
    output = np.empty((steps + 1, paths))
    output[0] = initial
    drift = (mean.to_numpy() - 0.5 * np.diag(covariance)) * dt
    for i in range(1, steps + 1):
        shocks = rng.standard_normal(asset_values.shape) @ root.T * np.sqrt(dt)
        asset_values *= np.exp(drift + shocks)
        output[i] = initial * (asset_values @ weights.to_numpy())
    return pd.DataFrame(output, index=pd.Index(np.linspace(0, years, steps + 1), name="years"))


def lump_sum_vs_dca(
    prices: pd.Series, budget: float = 12000, installments: int = 12
) -> pd.DataFrame:
    """Same cash available initially; DCA invests at evenly spaced observed closes, idle cash earns zero."""
    prices = series(prices, positive=True, missing=False)
    finite(budget, "budget", minimum=0)
    window_size(installments)
    if installments > len(prices):
        raise ValueError("installments exceed available bars")
    dates = set(np.linspace(0, len(prices) - 1, installments, dtype=int))
    cash, shares, dca = budget, 0.0, []
    for i, price in enumerate(prices):
        if i in dates:
            amount = min(budget / installments, cash)
            cash -= amount
            shares += amount / price
        dca.append(cash + shares * price)
    return pd.DataFrame(
        {"lump_sum": budget * prices / prices.iloc[0], "dca": dca}, index=prices.index
    )
