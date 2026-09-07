from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import series, window_size
from finance.indicators import rsi


@dataclass(frozen=True)
class ForecastEvaluation:
    predictions: pd.DataFrame
    metrics: pd.DataFrame
    training_end: object
    test_start: object


def _scores(predictions: pd.DataFrame) -> pd.DataFrame:
    actual = predictions["actual"]
    rows = {}
    for name in predictions.columns.drop("actual"):
        errors = predictions[name] - actual
        rows[name] = {"mae": errors.abs().mean(), "rmse": np.sqrt((errors**2).mean())}
    return pd.DataFrame(rows).T


def forecast_features(
    close: pd.Series, lags: int = 5, horizon: int = 1
) -> tuple[pd.DataFrame, pd.Series]:
    """Features known at close t, target close[t+h]/close[t]-1. Keep the final unknown labels missing."""
    close = series(close, positive=True, missing=False)
    window_size(lags)
    window_size(horizon)
    change = close.pct_change(fill_method=None)
    features = pd.DataFrame({f"return_lag_{lag}": change.shift(lag) for lag in range(lags)})
    features["rsi"] = rsi(close) / 100
    features["volatility"] = change.rolling(20).std()
    features["distance_sma"] = close / close.rolling(20).mean() - 1
    target = (close.shift(-horizon) / close - 1).rename("target")
    return features, target


def evaluate_forecast(
    close: pd.Series,
    *,
    horizon: int = 1,
    train_fraction: float = 0.75,
    model: str = "ridge",
    seed: int = 0,
) -> ForecastEvaluation:
    """Fixed-model chronological holdout with purged labels and a zero-return baseline."""
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.neural_network import MLPRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVR

    if not 0.2 < train_fraction < 0.95:
        raise ValueError("train_fraction must be between .2 and .95")
    features, target = forecast_features(close, horizon=horizon)
    data = features.join(target).dropna()
    split = int(len(data) * train_fraction)
    train, test = data.iloc[: split - horizon], data.iloc[split:]
    if len(train) < 40 or len(test) < 10:
        raise ValueError("insufficient history after warmup, purging and chronological split")
    estimators = {
        "ridge": Ridge(alpha=1),
        "forest": RandomForestRegressor(
            n_estimators=100, max_depth=4, min_samples_leaf=10, random_state=seed
        ),
        "boosting": HistGradientBoostingRegressor(
            max_iter=100, max_leaf_nodes=7, early_stopping=False, random_state=seed
        ),
        "svr": SVR(C=0.1),
        "mlp": MLPRegressor(
            hidden_layer_sizes=(16,), max_iter=1000, shuffle=False, random_state=seed
        ),
    }
    if model not in estimators:
        raise ValueError(f"model must be one of {list(estimators)}")
    pipeline = make_pipeline(StandardScaler(), estimators[model])
    columns = features.columns
    pipeline.fit(train[columns], train.target)
    predictions = pd.DataFrame(
        {"actual": test.target, model: pipeline.predict(test[columns]), "zero_return": 0.0},
        index=test.index,
    )
    return ForecastEvaluation(predictions, _scores(predictions), train.index[-1], test.index[0])


def evaluate_arima(
    close: pd.Series, train_fraction: float = 0.8, order: tuple[int, int, int] = (1, 1, 0)
) -> ForecastEvaluation:
    """Fixed-origin price forecast compared with persistence at that same origin."""
    from statsmodels.tsa.arima.model import ARIMA

    close = series(close, positive=True, missing=False)
    if (
        not 0.2 < train_fraction < 0.95
        or len(order) != 3
        or any(not isinstance(x, int) or x < 0 for x in order)
    ):
        raise ValueError("invalid split or ARIMA order")
    split = int(len(close) * train_fraction)
    train, test = close.iloc[:split], close.iloc[split:]
    if len(train) < 40 or len(test) < 10:
        raise ValueError("insufficient chronological history")
    fitted = ARIMA(train.to_numpy(), order=order).fit()
    if not fitted.mle_retvals.get("converged", True):
        raise ValueError("ARIMA failed to converge")
    predictions = pd.DataFrame(
        {"actual": test, "arima": fitted.forecast(len(test)), "persistence": train.iloc[-1]},
        index=test.index,
    )
    return ForecastEvaluation(predictions, _scores(predictions), train.index[-1], test.index[0])


def evaluate_direction(close: pd.Series, train_fraction: float = 0.75) -> ForecastEvaluation:
    """Gaussian naive Bayes experiment with held-out Brier/log-loss and training-prior baseline."""
    from sklearn.metrics import log_loss
    from sklearn.naive_bayes import GaussianNB

    features, target = forecast_features(close)
    data = features.join(target).dropna()
    if not 0.2 < train_fraction < 0.95:
        raise ValueError("invalid train_fraction")
    split = int(len(data) * train_fraction)
    train, test = data.iloc[: split - 1], data.iloc[split:]
    if len(train) < 40 or len(test) < 10:
        raise ValueError("insufficient history")
    y_train, y_test = (train.target > 0).astype(int), (test.target > 0).astype(int)
    if y_train.nunique() != 2:
        raise ValueError("training data must include both directions")
    fitted = GaussianNB().fit(train[features.columns], y_train)
    predictions = pd.DataFrame(
        {
            "actual": y_test,
            "gaussian_nb": fitted.predict_proba(test[features.columns])[:, 1],
            "prior": y_train.mean(),
        },
        index=test.index,
    )
    metrics = pd.DataFrame(
        {
            name: {
                "brier": ((predictions[name] - y_test) ** 2).mean(),
                "log_loss": log_loss(y_test, predictions[name], labels=[0, 1]),
            }
            for name in ["gaussian_nb", "prior"]
        }
    ).T
    return ForecastEvaluation(predictions, metrics, train.index[-1], test.index[0])
