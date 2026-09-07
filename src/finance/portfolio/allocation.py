from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import finite, frame, series, window_size


def _inputs(mean: pd.Series, covariance: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    mean = series(mean.sort_index(), missing=False)
    covariance = frame(covariance.sort_index().sort_index(axis=1))
    if not mean.index.equals(covariance.index) or not mean.index.equals(covariance.columns):
        raise ValueError("mean returns and covariance must have matching asset labels")
    values = covariance.to_numpy()
    if not np.allclose(values, values.T, atol=1e-12) or np.linalg.eigvalsh(values).min() < -1e-10:
        raise ValueError("covariance must be symmetric positive semidefinite")
    return mean, covariance


def _weights(weights: pd.Series, labels: pd.Index) -> pd.Series:
    if (
        not isinstance(weights, pd.Series)
        or not weights.index.is_unique
        or set(weights.index) != set(labels)
    ):
        raise ValueError("weights must match asset labels")
    weights = weights.reindex(labels).astype(float)
    if (
        not np.isfinite(weights).all()
        or (weights < 0).any()
        or not np.isclose(weights.sum(), 1, atol=1e-8)
    ):
        raise ValueError("long-only weights must be nonnegative and sum to one")
    return weights


def portfolio_statistics(
    weights: pd.Series, mean: pd.Series, covariance: pd.DataFrame, *, risk_free: float = 0
) -> pd.Series:
    """Mean/covariance and risk-free must use the same time unit (usually annual)."""
    mean, covariance = _inputs(mean, covariance)
    weights = _weights(weights, mean.index)
    finite(risk_free, "risk_free")
    expected = float(weights @ mean)
    volatility = float(np.sqrt(max(0, weights @ covariance @ weights)))
    return pd.Series(
        {
            "return": expected,
            "volatility": volatility,
            "sharpe": (expected - risk_free) / volatility if volatility > 0 else np.nan,
        }
    )


def portfolio_returns(asset_returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Constant-weight rebalanced returns, before costs; use backtest for actual execution."""
    asset_returns = frame(asset_returns)
    if (asset_returns < -1).any().any():
        raise ValueError("simple returns cannot be below -100%")
    return (asset_returns @ _weights(weights, asset_returns.columns)).rename("portfolio_return")


@dataclass(frozen=True)
class Allocation:
    weights: pd.Series
    statistics: pd.Series


def optimize(
    mean: pd.Series,
    covariance: pd.DataFrame,
    *,
    objective: str = "minimum_variance",
    risk_free: float = 0,
    bounds: tuple[float, float] = (0, 1),
    target_return: float | None = None,
) -> Allocation:
    """Long-only SLSQP optimization, with explicit solver and constraint verification."""
    from scipy.optimize import minimize

    mean, covariance = _inputs(mean, covariance)
    lower, upper = bounds
    finite(lower, "lower", minimum=0)
    finite(upper, "upper", minimum=lower)
    finite(risk_free, "risk_free")
    size = len(mean)
    if upper > 1 or size * lower > 1 + 1e-12 or size * upper < 1 - 1e-12:
        raise ValueError("infeasible bounds")
    if objective not in ("minimum_variance", "maximum_sharpe"):
        raise ValueError("objective must be minimum_variance or maximum_sharpe")
    mu, cov = mean.to_numpy(), covariance.to_numpy()
    if objective == "maximum_sharpe" and mu.max() <= risk_free:
        raise ValueError("maximum Sharpe requires an asset with positive expected excess return")

    def loss(weights):
        variance = float(weights @ cov @ weights)
        if objective == "minimum_variance":
            return variance
        return -(weights @ mu - risk_free) / np.sqrt(max(variance, 1e-18))

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    if target_return is not None:
        finite(target_return, "target_return")
        constraints.append({"type": "eq", "fun": lambda w: w @ mu - target_return})
    result = minimize(
        loss,
        np.full(size, 1 / size),
        method="SLSQP",
        bounds=[bounds] * size,
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1000},
    )
    if not result.success:
        raise ValueError(f"portfolio optimization failed: {result.message}")
    weights = pd.Series(result.x, index=mean.index)
    if (
        (weights < lower - 1e-7).any()
        or (weights > upper + 1e-7).any()
        or abs(weights.sum() - 1) > 1e-7
    ):
        raise ValueError("solver returned constraint-violating weights")
    if target_return is not None and abs(weights @ mean - target_return) > 1e-7:
        raise ValueError("solver did not meet target return")
    weights = weights.clip(lower=0)
    weights /= weights.sum()
    return Allocation(weights, portfolio_statistics(weights, mean, covariance, risk_free=risk_free))


def efficient_frontier(mean: pd.Series, covariance: pd.DataFrame, points: int = 20) -> pd.DataFrame:
    """Efficient branch from the minimum-variance return to the highest asset return."""
    window_size(points, 2)
    minimum = optimize(mean, covariance)
    targets = np.linspace(minimum.statistics["return"], mean.max(), points)
    allocations = [optimize(mean, covariance, target_return=target) for target in targets]
    return pd.DataFrame(
        [
            a.statistics.to_dict() | {f"weight_{k}": v for k, v in a.weights.items()}
            for a in allocations
        ]
    )


def random_allocations(
    mean: pd.Series, covariance: pd.DataFrame, count: int = 1000, seed: int = 0
) -> pd.DataFrame:
    mean, covariance = _inputs(mean, covariance)
    window_size(count)
    weights = np.random.default_rng(seed).dirichlet(np.ones(len(mean)), count)
    result = pd.DataFrame(weights, columns=mean.index)
    result["return"] = weights @ mean.to_numpy()
    result["volatility"] = np.sqrt(
        np.maximum(0, np.einsum("ij,jk,ik->i", weights, covariance.to_numpy(), weights))
    )
    return result


def discrete_allocation(
    weights: pd.Series, prices: pd.Series, budget: float
) -> tuple[pd.Series, float]:
    """Whole-share floor allocation; returns unspent cash without overspending."""
    prices = series(prices.sort_index(), positive=True, missing=False)
    weights = _weights(weights, prices.index)
    finite(budget, "budget", minimum=0)
    quantities = np.floor(weights * budget / prices).astype(int)
    return quantities, float(budget - quantities @ prices)
