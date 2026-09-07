from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import aligned, finite, frame, series


@dataclass(frozen=True)
class RegressionResult:
    coefficients: pd.Series
    residuals: pd.Series
    r_squared: float


def ols(y: pd.Series, factors: pd.DataFrame) -> RegressionResult:
    """OLS with intercept; factors and response must be explicitly aligned and complete."""
    y, factors = series(y, missing=False), frame(factors)
    if not y.index.equals(factors.index) or "intercept" in factors:
        raise ValueError("align inputs and reserve the name intercept")
    design = np.column_stack([np.ones(len(y)), factors.to_numpy()])
    if len(y) <= design.shape[1] or np.linalg.matrix_rank(design) < design.shape[1]:
        raise ValueError("insufficient observations or rank-deficient factors")
    coefficients, *_ = np.linalg.lstsq(design, y.to_numpy(), rcond=None)
    residuals = y - design @ coefficients
    total = ((y - y.mean()) ** 2).sum()
    score = 1 - (residuals**2).sum() / total if total > 0 else np.nan
    return RegressionResult(
        pd.Series(coefficients, index=["intercept", *factors.columns]), residuals, float(score)
    )


def capm(
    asset_returns: pd.Series, market_returns: pd.Series, *, risk_free: float = 0, periods: int = 252
) -> pd.Series:
    """CAPM on simple excess returns; annual risk-free and arithmetic expected return."""
    asset_returns, market_returns = aligned(asset_returns, market_returns)
    finite(risk_free, "risk_free")
    if risk_free <= -1 or periods <= 0:
        raise ValueError("require risk_free > -1 and periods > 0")
    rate = (1 + risk_free) ** (1 / periods) - 1
    fitted = ols(asset_returns - rate, (market_returns - rate).to_frame("market"))
    beta = fitted.coefficients["market"]
    return pd.Series(
        {
            "alpha": fitted.coefficients["intercept"] * periods,
            "beta": beta,
            "expected_return": risk_free + beta * (market_returns.mean() * periods - risk_free),
            "r_squared": fitted.r_squared,
        }
    )


def correlation_pairs(values: pd.DataFrame) -> pd.DataFrame:
    correlations = frame(values).corr()
    rows = [
        (a, b, correlations.loc[a, b])
        for i, a in enumerate(values)
        for b in values.columns[i + 1 :]
    ]
    result = pd.DataFrame(rows, columns=["asset_a", "asset_b", "correlation"])
    return result.sort_values("correlation", key=abs, ascending=False, ignore_index=True)
