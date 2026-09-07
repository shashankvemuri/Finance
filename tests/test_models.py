import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from finance.models import (
    anomaly_scores,
    cluster_assets,
    cluster_features,
    evaluate_arima,
    evaluate_direction,
    evaluate_forecast,
    forecast_features,
    partial_correlations,
    pca,
)

pytest.importorskip("sklearn")


def test_features_do_not_contain_future(ohlcv):
    full, target = forecast_features(ohlcv.close, horizon=5)
    prefix, _ = forecast_features(ohlcv.close.iloc[:400], horizon=5)
    assert_allclose(full.iloc[:400], prefix, equal_nan=True)
    assert target.iloc[-5:].isna().all()
    assert target.iloc[100] == pytest.approx(ohlcv.close.iloc[105] / ohlcv.close.iloc[100] - 1)


@pytest.mark.parametrize("model", ["ridge", "forest", "boosting", "svr", "mlp"])
def test_chronological_evaluation_and_scaling_isolation(ohlcv, model):
    result = evaluate_forecast(ohlcv.close, horizon=5, model=model)
    assert result.training_end < result.test_start
    assert ohlcv.index.get_loc(result.test_start) - ohlcv.index.get_loc(result.training_end) > 5
    assert result.predictions.notna().all().all()
    assert (result.metrics >= 0).all().all()
    assert result.metrics.loc["zero_return", "mae"] == pytest.approx(
        result.predictions.actual.abs().mean()
    )
    # A final held-out shock must not change earlier predictions from the fixed training fit.
    altered = ohlcv.close.copy()
    altered.iloc[-1] *= 2
    other = evaluate_forecast(altered, horizon=5, model=model)
    assert_allclose(result.predictions[model].iloc[:-5], other.predictions[model].iloc[:-5])


def test_arima_and_probability(ohlcv):
    pytest.importorskip("statsmodels")
    result = evaluate_arima(ohlcv.close, order=(0, 1, 0))
    # A driftless ARIMA(0,1,0) is precisely the random-walk/persistence baseline.
    assert_allclose(result.predictions.arima, result.predictions.persistence, rtol=1e-6)
    direction = evaluate_direction(ohlcv.close)
    assert direction.predictions.gaussian_nb.between(0, 1).all()
    assert (direction.metrics.brier >= 0).all()


def test_structure_axes_and_invariants(ohlcv):
    rng = np.random.default_rng(4)
    data = pd.DataFrame(
        rng.normal(0, 0.02, (300, 5)), index=ohlcv.index[:300], columns=list("abcde")
    )
    result = pca(data, 3)
    assert result.loadings.shape == (5, 3)
    assert result.scores.shape == (300, 3)
    assert result.explained_variance.sum() <= 1 + 1e-10
    assert_allclose(result.loadings.T @ result.loadings, np.eye(3), atol=1e-12)
    for components in [None, 2]:
        groups = cluster_assets(data, 2, components=components)
        assert groups.index.equals(data.columns)
        assert groups.nunique() == 2
    assert cluster_assets(data, 2, components=2, method="mixture").nunique() == 2
    assert cluster_features(data.T, 2).shape == (5,)
    partial = partial_correlations(data)
    assert_allclose(np.diag(partial), 1)
    assert_allclose(partial, partial.T)
    assert (np.abs(partial) <= 1 + 1e-12).all().all()
    scores = anomaly_scores(data.iloc[:200], data.iloc[200:])
    assert scores.shape == (100,)
    with pytest.raises(ValueError):
        anomaly_scores(data.iloc[200:], data.iloc[:100])
