import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from finance.analytics import (
    correlation_pairs,
    distribution,
    fundamental_ratios,
    net_positioning,
    return_probability,
    seasonality,
    sentiment,
)
from finance.models import cointegration_pairs
from finance.strategies import (
    bollinger_reversion,
    breakout,
    lag_reversal,
    ribbon_trend,
    rsi_reversion,
    threshold_reversion,
)


@pytest.mark.parametrize("name", ["bollinger", "breakout", "ribbon", "rsi", "lag"])
def test_strategy_prefix_and_state(ohlcv, name):
    def run(p):
        if name == "bollinger":
            return bollinger_reversion(p.close, short=True)
        if name == "breakout":
            return breakout(p.high, p.low, p.close)
        if name == "ribbon":
            return ribbon_trend(p.close)
        if name == "rsi":
            return rsi_reversion(p.close, short=True)
        return lag_reversal(p.high, p.low, p.close)

    full = run(ohlcv)
    assert full.isin([-1, 0, 1]).all()
    assert_allclose(full.iloc[:300], run(ohlcv.iloc[:300]))
    assert full.iloc[:5].eq(0).all()


def test_threshold_state_hand_fixture():
    result = threshold_reversion(pd.Series([0.0, -3, -1, 0, 3, 1, 0]), -2, 2, 0, short=True)
    assert_allclose(result, [0, 1, 1, 0, -1, -1, 0])


def test_descriptive_statistics(ohlcv):
    data = pd.Series([-1.0, 0, 1])
    assert distribution(data)["mean"] == 0
    assert return_probability(data, -1, 1) == pytest.approx(0.682689492)
    assert_allclose(net_positioning(pd.Series([40.0]), pd.Series([20.0]), pd.Series([100.0])), 0.2)
    ratios = fundamental_ratios(
        price=100, earnings_per_share=5, book_value_per_share=20, annual_dividend=3
    )
    assert_allclose(ratios, [20, 5, 0.03])
    pairs = correlation_pairs(pd.DataFrame({"a": data, "b": data * 2, "c": -data}))
    assert len(pairs) == 3
    assert_allclose(pairs.correlation.abs(), 1)
    seasonal = seasonality(ohlcv.close)
    assert seasonal["count"].sum() > 12
    assert seasonal.win_rate.between(0, 1).all()


def test_sentiment():
    pytest.importorskip("vaderSentiment")
    result = sentiment(["Great profit and excellent growth!", "Terrible losses and bankruptcy."])
    assert result.compound.iloc[0] > 0 and result.compound.iloc[1] < 0


def test_cointegration_reference():
    pytest.importorskip("statsmodels")
    rng = np.random.default_rng(6)
    x = np.cumsum(rng.normal(0, 0.01, 300))
    data = pd.DataFrame(
        {
            "a": np.exp(x + 5),
            "b": np.exp(x + 4 + rng.normal(0, 0.001, 300)),
            "c": np.exp(np.cumsum(rng.normal(0, 0.01, 300)) + 5),
        }
    )
    result = cointegration_pairs(data)
    assert len(result) == 3
    assert (result.adjusted_p_value >= result.p_value).all()
    row = result[(result["first"] == "a") & (result["second"] == "b")].iloc[0]
    assert row.adjusted_p_value < 0.01
