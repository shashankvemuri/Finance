"""Statistical diagnostics and chronological regime inference."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import frame, series, window_size


@dataclass(frozen=True)
class FactorResult:
    loadings: pd.DataFrame
    communalities: pd.Series
    diagnostics: pd.Series


def factor_analysis(returns: pd.DataFrame, factors: int = 2) -> FactorResult:
    """Maximum-likelihood factor analysis of standardized observations; unrotated loadings."""
    from scipy.stats import chi2
    from sklearn.decomposition import FactorAnalysis
    from sklearn.preprocessing import StandardScaler

    returns = frame(returns)
    window_size(factors)
    n, p = returns.shape
    if not 1 <= factors < p or n <= p + 2 or (returns.std() == 0).any():
        raise ValueError(
            "require fewer factors than nonconstant assets and more observations than assets"
        )
    correlation = returns.corr().to_numpy(copy=True)
    sign, logdet = np.linalg.slogdet(correlation)
    if sign <= 0 or np.linalg.cond(correlation) > 1e10:
        raise ValueError("factor diagnostics require nonsingular correlation")
    inverse = np.linalg.inv(correlation)
    partial = -inverse / np.sqrt(np.outer(np.diag(inverse), np.diag(inverse)))
    np.fill_diagonal(partial, 0)
    np.fill_diagonal(correlation, 0)
    numerator = (correlation**2).sum()
    kmo = numerator / (numerator + (partial**2).sum()) if numerator else np.nan
    statistic = -(n - 1 - (2 * p + 5) / 6) * logdet
    scaled = StandardScaler().fit_transform(returns)
    model = FactorAnalysis(n_components=factors, random_state=0, max_iter=2000).fit(scaled)
    if model.n_iter_ >= 2000:
        raise ValueError("factor analysis did not converge")
    loadings = pd.DataFrame(
        model.components_.T,
        index=returns.columns,
        columns=[f"factor_{i + 1}" for i in range(factors)],
    )
    return FactorResult(
        loadings,
        (loadings**2).sum(axis=1).rename("communality"),
        pd.Series(
            {
                "kmo": kmo,
                "bartlett_statistic": statistic,
                "bartlett_p_value": chi2.sf(statistic, p * (p - 1) / 2),
            }
        ),
    )


def student_t_fit(values: pd.Series) -> pd.Series:
    """MLE location/scale/df; scale is not standard deviation. Descriptive fit only."""
    from scipy.stats import t

    values = series(values, missing=False)
    if len(values) < 30 or values.std() == 0:
        raise ValueError("at least 30 nonconstant observations required")
    degrees, location, scale = t.fit(values.to_numpy())
    return pd.Series(
        {
            "df": degrees,
            "location": location,
            "scale": scale,
            "std": scale * np.sqrt(degrees / (degrees - 2)) if degrees > 2 else np.inf,
            "q01": t.ppf(0.01, degrees, loc=location, scale=scale),
            "q99": t.ppf(0.99, degrees, loc=location, scale=scale),
        }
    )


def volatility_regimes(
    close: pd.Series,
    *,
    train_fraction: float = 0.7,
    regimes: int = 2,
    window: int = 20,
    seed: int = 0,
) -> pd.DataFrame:
    """Mixture fitted to past rolling volatility; held-out rows contain causal state probabilities."""
    from sklearn.mixture import GaussianMixture

    close = series(close, positive=True, missing=False)
    window_size(window, 2)
    window_size(regimes, 2)
    if not 0.2 < train_fraction < 0.9:
        raise ValueError("invalid chronological split")
    volatility = close.pct_change(fill_method=None).rolling(window).std().dropna()
    if (volatility <= 0).any():
        raise ValueError("positive rolling volatility required")
    split = int(len(volatility) * train_fraction)
    train, test = volatility.iloc[:split], volatility.iloc[split:]
    if len(train) < max(40, regimes * 10) or len(test) < 10:
        raise ValueError("insufficient training/test observations")
    model = GaussianMixture(n_components=regimes, random_state=seed, n_init=5).fit(
        np.log(train).to_numpy()[:, None]
    )
    if not model.converged_:
        raise ValueError("volatility mixture did not converge")
    order = np.argsort(model.means_[:, 0])
    probabilities = model.predict_proba(np.log(test).to_numpy()[:, None])[:, order]
    result = pd.DataFrame(
        probabilities, index=test.index, columns=[f"regime_{i + 1}" for i in range(regimes)]
    )
    result["volatility"] = test
    result["regime"] = probabilities.argmax(axis=1) + 1
    result.attrs.update(training_end=train.index[-1], ordering="ascending training log-volatility")
    return result


def partial_correlations_cv(returns: pd.DataFrame, folds: int = 5) -> pd.DataFrame:
    """Descriptive conditional-dependence network with chronological alpha selection."""
    from sklearn.covariance import GraphicalLassoCV
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.preprocessing import StandardScaler

    returns = frame(returns)
    window_size(folds, 2)
    if len(returns) < folds * 10 or (returns.std() == 0).any():
        raise ValueError("insufficient nonconstant observations")
    # Common scale uses the initial fold only; later validation observations do not fit it.
    cv = TimeSeriesSplit(n_splits=folds)
    first_train, _ = next(cv.split(returns))
    scaler = StandardScaler().fit(returns.iloc[first_train])
    fitted = GraphicalLassoCV(cv=cv, max_iter=500).fit(scaler.transform(returns))
    if fitted.n_iter_ >= 500:
        raise ValueError("graphical lasso did not converge")
    precision = fitted.precision_
    result = -precision / np.sqrt(np.outer(np.diag(precision), np.diag(precision)))
    np.fill_diagonal(result, 1)
    output = pd.DataFrame(result, index=returns.columns, columns=returns.columns)
    output.attrs["alpha"] = fitted.alpha_
    return output


def arima_forecast(
    close: pd.Series,
    steps: int = 10,
    *,
    order: tuple[int, int, int] = (1, 1, 0),
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Future observation steps, not guessed exchange dates; model-based price intervals."""
    from statsmodels.tsa.arima.model import ARIMA

    close = series(close, positive=True, missing=False)
    window_size(steps)
    if (
        len(close) < 40
        or not 0 < confidence < 1
        or len(order) != 3
        or any(not isinstance(x, int) or x < 0 for x in order)
    ):
        raise ValueError("invalid history, confidence or ARIMA order")
    model = ARIMA(close.to_numpy(), order=order).fit()
    if not model.mle_retvals.get("converged", True):
        raise ValueError("ARIMA failed to converge")
    forecast = model.get_forecast(steps)
    intervals = forecast.conf_int(alpha=1 - confidence)
    result = pd.DataFrame(
        {"forecast": forecast.predicted_mean, "lower": intervals[:, 0], "upper": intervals[:, 1]},
        index=pd.RangeIndex(1, steps + 1, name="step"),
    )
    result.attrs.update(as_of=close.index[-1], confidence=confidence, order=order)
    return result


def arima_diagnostics(
    close: pd.Series, *, order: tuple[int, int, int] = (1, 1, 0), seasonal_period: int = 21
) -> tuple[pd.Series, pd.DataFrame]:
    """ADF, residual Ljung–Box, and retrospective STL decomposition; not forecast features."""
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import STL
    from statsmodels.tsa.stattools import adfuller

    close = series(close, positive=True, missing=False)
    window_size(seasonal_period, 2)
    if len(close) < max(60, 2 * seasonal_period) or close.std() == 0:
        raise ValueError("insufficient nonconstant history")
    model = ARIMA(close.to_numpy(), order=order).fit()
    if not model.mle_retvals.get("converged", True):
        raise ValueError("ARIMA failed to converge")
    residuals = model.resid[max(order[1], 1) :]
    lb = acorr_ljungbox(residuals, lags=[10], return_df=True)
    stl = STL(close, period=seasonal_period, robust=True).fit()
    diagnostics = pd.Series(
        {
            "adf_price_p_value": adfuller(close)[1],
            "adf_difference_p_value": adfuller(close.diff().dropna())[1],
            "residual_ljung_box_p_value": lb.lb_pvalue.iloc[0],
            "aic": model.aic,
            "bic": model.bic,
        }
    )
    return diagnostics, pd.DataFrame(
        {"trend": stl.trend, "seasonal": stl.seasonal, "residual": stl.resid}, index=close.index
    )


def select_arima_order(
    close: pd.Series,
    orders: tuple[tuple[int, int, int], ...] = ((0, 1, 0), (1, 1, 0), (0, 1, 1)),
    *,
    train_fraction: float = 0.8,
) -> pd.DataFrame:
    """Rank candidate orders by training BIC. Failures remain visible; holdout is never fitted."""
    from statsmodels.tsa.arima.model import ARIMA

    close = series(close, positive=True, missing=False)
    if not orders or not 0.2 < train_fraction < 0.9:
        raise ValueError("orders and chronological split required")
    training = close.iloc[: int(len(close) * train_fraction)]
    if len(training) < 40:
        raise ValueError("insufficient training history")
    rows = []
    for order in orders:
        if len(order) != 3 or any(not isinstance(x, int) or x < 0 for x in order):
            raise ValueError("each order must contain three nonnegative integers")
        try:
            fitted = ARIMA(training.to_numpy(), order=order).fit()
            converged = fitted.mle_retvals.get("converged", True)
            rows.append(
                {
                    "order": order,
                    "bic": fitted.bic if converged else np.nan,
                    "status": "converged" if converged else "not converged",
                }
            )
        except (ValueError, np.linalg.LinAlgError) as exc:
            rows.append({"order": order, "bic": np.nan, "status": str(exc)})
    result = pd.DataFrame(rows).sort_values("bic", ignore_index=True)
    result.attrs["training_end"] = training.index[-1]
    return result
