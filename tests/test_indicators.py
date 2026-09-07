import inspect

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

import finance.indicators as ind


def test_moving_averages_hand_values():
    x = pd.Series([1.0, 2, 3, 4, 5])
    assert_allclose(ind.sma(x, 3), [np.nan, np.nan, 2, 3, 4], equal_nan=True)
    assert_allclose(ind.wma(x, 3), [np.nan, np.nan, 14 / 6, 20 / 6, 26 / 6], equal_nan=True)
    assert_allclose(ind.smma(x, 3), [np.nan, np.nan, 2, 8 / 3, 31 / 9], equal_nan=True)
    assert_allclose(ind.ema(x, 3), [np.nan, np.nan, 2.25, 3.125, 4.0625], equal_nan=True)
    assert ind.trima(x, 5).iloc[-1] == 3
    assert_allclose(ind.rolling_regression(x, 3).slope.dropna(), 1)
    assert_allclose(ind.rolling_regression(x, 3).fitted.dropna(), [3, 4, 5])


def test_rsi_published_wilder_fixture():
    # Wilder/StockCharts worksheet, first RSI uses changes between these 15 prices.
    close = pd.Series(
        [
            44.34,
            44.09,
            44.15,
            43.61,
            44.33,
            44.83,
            45.10,
            45.42,
            45.84,
            46.08,
            45.89,
            46.03,
            45.61,
            46.28,
            46.28,
            46.00,
        ]
    )
    actual = ind.rsi(close)
    assert actual.iloc[:14].isna().all()
    assert actual.iloc[14] == pytest.approx(70.464135, abs=1e-6)
    assert actual.iloc[15] == pytest.approx(66.249619, abs=1e-6)


def test_ranges_and_volume_by_hand():
    high, low, close = pd.Series([11.0, 13, 12]), pd.Series([9.0, 10, 8]), pd.Series([10.0, 12, 9])
    volume = pd.Series([100.0, 200, 100])
    assert_allclose(ind.true_range(high, low, close), [2, 3, 4])
    assert ind.atr(high, low, close, 3).iloc[-1] == 3
    assert ind.stochastic(high, low, close, 3).k.iloc[-1] == 20
    assert ind.williams_r(high, low, close, 3).iloc[-1] == -80
    assert_allclose(ind.vwap(close, volume), [10, 34 / 3, 10.75])
    assert ind.vwma(close, volume, 3).iloc[-1] == 10.75
    assert_allclose(ind.pvt(close, volume), [0, 40, 15], atol=1e-12)
    assert_allclose(ind.pvi(close, volume), [1000, 1200, 1200])
    assert_allclose(ind.obv(close, volume), [0, 200, 100])
    assert ind.mfi(high, low, close, volume, 2).iloc[-1] == pytest.approx(
        100 * (35 / 3 * 200) / (35 / 3 * 200 + 29 / 3 * 100)
    )


def test_flat_and_zero_volume():
    x = pd.Series(np.ones(70) * 10)
    zero = x * 0
    assert_allclose(ind.rsi(x).dropna(), 50)
    assert_allclose(ind.stochastic(x, x, x).k.dropna(), 50)
    assert_allclose(ind.cci(x, x, x).dropna(), 0)
    assert_allclose(ind.adx(x, x, x).adx.dropna(), 0)
    assert_allclose(ind.accumulation_distribution(x, x, x, zero), 0)
    assert ind.vwap(x, zero).isna().all()
    assert ind.vwma(x, zero).isna().all()
    assert_allclose(ind.rsi(pd.Series(np.arange(1.0, 50))).dropna(), 100)
    assert_allclose(ind.rsi(pd.Series(np.arange(50.0, 1, -1))).dropna(), 0)


def test_session_reset_and_missing_data():
    price = pd.Series([10.0, 20, 30, 40])
    volume = pd.Series([1.0, 3, 1, 3])
    sessions = pd.Series(["a", "a", "b", "b"])
    assert_allclose(ind.vwap(price, volume, sessions), [10, 17.5, 30, 37.5])
    assert ind.smma(pd.Series([1.0, 2, 3, np.nan, 4, 5, 6]), 3).iloc[-1] == 5
    with pytest.raises(ValueError, match="identical"):
        ind.vwma(price, volume.set_axis([1, 2, 3, 4]), 2)
    with pytest.raises(ValueError):
        ind.vwap(price, -volume)


def test_levels_timing():
    high, low, close = pd.Series([12.0, 99]), pd.Series([8.0, 90]), pd.Series([11.0, 95])
    levels = ind.pivot_points(high, low, close)
    assert levels.iloc[0].isna().all()
    assert levels["pivot"].iloc[1] == pytest.approx(31 / 3)
    assert levels.r1.iloc[1] == pytest.approx(38 / 3)
    cam = ind.pivot_points(high, low, close, method="camarilla")
    assert cam.r4.iloc[1] == pytest.approx(13.2)
    assert cam.s4.iloc[1] == pytest.approx(8.8)
    assert ind.fibonacci_levels(10, 20).loc[0.618] == pytest.approx(13.82)
    levels = ind.confirmed_extrema(pd.Series([1.0, 2, 5, 3, 1]), pd.Series([0.5, 1, 2, 1, 0.5]), 2)
    assert levels.resistance.iloc[:4].isna().all()
    assert levels.resistance.iloc[4] == 5
    highs = pd.Series([10.0, 9, 8, 7, 12, 11, 10, 9])
    assert_allclose(
        ind.green_line(highs), [np.nan, np.nan, np.nan, 10, 10, 10, 10, 12], equal_nan=True
    )


REFERENCE_FUNCTIONS = [
    ("sma", lambda t, p: t.trend.sma_indicator(p.close, 20)),
    ("ema", lambda t, p: t.trend.ema_indicator(p.close, 20)),
    ("wma", lambda t, p: t.trend.wma_indicator(p.close, 20)),
    ("cci", lambda t, p: t.trend.cci(p.high, p.low, p.close, 20)),
    ("pvt", lambda t, p: t.volume.volume_price_trend(p.close, p.volume)),
    (
        "chaikin_money_flow",
        lambda t, p: t.volume.chaikin_money_flow(p.high, p.low, p.close, p.volume, 20),
    ),
    ("force_index", lambda t, p: t.volume.force_index(p.close, p.volume, 13)),
    ("bollinger_bands", lambda t, p: t.volatility.bollinger_hband(p.close)),
    ("atr", lambda t, p: t.volatility.average_true_range(p.high, p.low, p.close)),
    ("stochastic", lambda t, p: t.momentum.stoch(p.high, p.low, p.close)),
    ("tsi", lambda t, p: t.momentum.tsi(p.close)),
    ("ultimate_oscillator", lambda t, p: t.momentum.ultimate_oscillator(p.high, p.low, p.close)),
    ("adx", lambda t, p: t.trend.adx(p.high, p.low, p.close)),
]


@pytest.mark.parametrize("name,reference", REFERENCE_FUNCTIONS)
def test_independent_ta_reference(ohlcv, name, reference):
    ta = pytest.importorskip("ta")
    function = getattr(ind, name)
    parameters = inspect.signature(function).parameters
    args = {k: ohlcv[k] for k in parameters if k in ohlcv}
    actual = function(**args)
    expected = reference(ta, ohlcv)
    column = {"bollinger_bands": "upper", "stochastic": "k", "adx": "adx"}.get(name)
    if column is not None:
        actual = actual[column]
    # ta uses a different missing-value convention before ATR/ADX initialize and at PVT t0.
    start = {"atr": 13, "adx": 27, "pvt": 1}.get(name, 0)
    assert_allclose(
        actual.iloc[start:], expected.iloc[start:], rtol=1e-10, atol=1e-8, equal_nan=True
    )


@pytest.mark.parametrize(
    "name",
    [
        n
        for n in ind.__all__
        if n
        not in (
            "fibonacci_levels",
            "breadth",
            "green_line",
            "arms_index",
            "mcclellan",
            "relative_price",
            "beta",
            "correlation",
            "covariance",
        )
    ],
)
def test_indicator_prefix_causality_and_structure(ohlcv, name):
    function = getattr(ind, name)
    mapping = {**{k: ohlcv[k] for k in ohlcv}, "price": ohlcv.close, "values": ohlcv.close}
    signature = inspect.signature(function)
    if any(
        k not in mapping and p.default is inspect.Parameter.empty
        for k, p in signature.parameters.items()
    ):
        pytest.fail(f"add explicit test input for {name}")
    args = {k: v for k, v in mapping.items() if k in signature.parameters}
    if name == "pivot_points":
        args.pop("open", None)
    result = function(**args)
    truncated = function(**{k: v.iloc[:400] for k, v in args.items()})
    assert result.index.equals(ohlcv.index)
    assert result.notna().to_numpy().any()
    assert not np.isinf(result.to_numpy()).any()
    assert_allclose(result.iloc[:400], truncated, equal_nan=True, atol=1e-9)


@pytest.mark.parametrize("window", [0, -1, 1.5, True])
def test_invalid_windows(window):
    with pytest.raises(ValueError):
        ind.sma(pd.Series([1.0, 2, 3]), window)


def test_breadth_and_relative(ohlcv):
    x = pd.Series([1.0, 2, 3, 2])
    y = pd.Series([3.0, 2, 1, 2])
    breadth = ind.breadth(pd.DataFrame({"a": x, "b": y}), 2)
    assert_allclose(breadth.advances.iloc[1:], [1, 1, 1])
    assert_allclose(breadth.new_highs.iloc[1:], [1, 1, 1])
    a = pd.Series([0.01, 0.02, -0.01, 0.04])
    b = 2 * a
    assert ind.beta(b, a, 4).iloc[-1] == pytest.approx(2)
    assert ind.correlation(a, b, 4).iloc[-1] == pytest.approx(1)
    assert ind.covariance(a, b, 4).iloc[-1] == pytest.approx(np.cov(a, b)[0, 1])
    assert_allclose(ind.relative_price(x, y), x / y)
    counts = pd.Series(np.arange(1.0, 101))
    assert ind.mcclellan(counts, counts).dropna().eq(0).all()
    assert_allclose(ind.arms_index(counts, counts, counts * 2, counts), 0.5)
