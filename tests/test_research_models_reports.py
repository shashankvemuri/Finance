import numpy as np
import pandas as pd
import pytest

from finance.integrations import Alpaca, email_report, preview_order
from finance.models import (
    arima_forecast,
    evaluate_prophet,
    evaluate_sequence,
    factor_analysis,
    forecast_latest,
    student_t_fit,
    volatility_regimes,
)
from finance.reports import export_table, network_gexf, research_report


def test_latest_forecast_uses_known_labels(ohlcv):
    pytest.importorskip("sklearn")
    result = forecast_latest(ohlcv.close, horizon=5)
    assert result.training_end == ohlcv.index[-6]
    assert result.as_of == ohlcv.index[-1]
    assert np.isfinite(result.predicted_return)
    assert result.implied_price == pytest.approx(
        ohlcv.close.iloc[-1] * (1 + result.predicted_return)
    )


def test_arima_random_walk_formula(ohlcv):
    pytest.importorskip("statsmodels")
    result = arima_forecast(ohlcv.close, 5, order=(0, 1, 0))
    assert np.allclose(result.forecast, ohlcv.close.iloc[-1])
    assert (result.lower < result.forecast).all() and (result.forecast < result.upper).all()
    assert (result.upper - result.lower).is_monotonic_increasing


def test_factor_known_one_factor_structure():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(45)
    common = rng.normal(size=2000)
    values = pd.DataFrame(
        {name: common + rng.normal(0, 0.3, 2000) for name in ["A", "B", "C", "D"]}
    )
    result = factor_analysis(values, 1)
    assert result.communalities.between(0.85, 0.97).all()
    assert result.diagnostics.kmo > 0.8
    assert result.diagnostics.bartlett_p_value < 0.001


def test_student_t_parameter_recovery():
    pytest.importorskip("scipy")
    rng = np.random.default_rng(23)
    sample = pd.Series(rng.standard_t(5, 20000) * 0.02 + 0.001)
    result = student_t_fit(sample)
    assert 4 < result.df < 6.5
    assert result.scale == pytest.approx(0.02, abs=0.001)
    assert result.location == pytest.approx(0.001, abs=0.001)
    assert result.q01 < result.location < result.q99


def test_regime_probabilities_and_training_boundary(ohlcv):
    pytest.importorskip("sklearn")
    result = volatility_regimes(ohlcv.close)
    assert np.allclose(result[["regime_1", "regime_2"]].sum(axis=1), 1)
    assert result.attrs["training_end"] < result.index[0]


@pytest.mark.parametrize("architecture", ["lstm", "cnn"])
def test_neural_baseline_and_chronology(architecture, ohlcv):
    pytest.importorskip("torch")
    result = evaluate_sequence(ohlcv.close.iloc[:180], architecture=architecture, epochs=2)
    assert result.training_end < result.test_start
    assert result.predictions.zero_return.eq(0).all()
    assert np.isfinite(result.metrics).all().all()


def test_prophet_chronology_and_baseline(ohlcv):
    pytest.importorskip("prophet")
    result = evaluate_prophet(ohlcv.close.iloc[:180])
    assert result.predictions.persistence.nunique() == 1
    assert result.training_end < result.test_start
    assert np.isfinite(result.metrics).all().all()


def test_exports_escape_content(tmp_path):
    data = pd.DataFrame(
        {"text": ["=1+1", "<script>alert(1)</script>"], "value": [1.0, -2.0]}, index=["A", "B"]
    )
    path = export_table(data, tmp_path / "report.csv")
    assert "'=1+1" in path.read_text()
    report = research_report({"Research": data}, tmp_path / "report.html")
    assert "<script>" not in report.read_text()
    assert "&lt;script&gt;" in report.read_text()
    corr = pd.DataFrame([[1, 0.5], [0.5, 1]], index=["A", "B"], columns=["A", "B"])
    path = network_gexf(corr, tmp_path / "network.gexf")
    from xml.etree import ElementTree

    root = ElementTree.parse(path)
    assert len(root.findall(".//{http://www.gexf.net/1.2draft}edge")) == 1


def test_order_preview_and_live_gate(monkeypatch):
    order = preview_order("AAPL", 2, "buy", 100, maximum_notional=250, client_order_id="signal-001")
    assert order.estimated_notional == 200
    with pytest.raises(ValueError):
        preview_order("AAPL", 3, "buy", 100, maximum_notional=250, client_order_id="signal-001")
    calls = []
    monkeypatch.setattr(
        Alpaca, "_request", lambda self, *args: calls.append(args) or {"id": "example"}
    )
    paper = Alpaca("key", "secret")
    assert paper.submit(order, limit_price=100)["id"] == "example"
    assert calls[0][2]["client_order_id"] == "signal-001"
    with pytest.raises(ValueError):
        Alpaca("key", "secret", paper=False).submit(order, limit_price=100)
    assert "secret" not in repr(paper)
    message = email_report("a@example.com", "b@example.com", "Preview", "Body")
    assert message["Subject"] == "Preview" and message.get_content().strip() == "Body"


def test_reconcile_partial_fill_and_unknown():
    from finance.integrations import reconcile_orders

    order = preview_order("AAPL", 2, "buy", 100, maximum_notional=250, client_order_id="one")
    result = reconcile_orders(
        [order],
        [
            {
                "client_order_id": "one",
                "status": "partially_filled",
                "filled_qty": "1",
                "filled_avg_price": "99",
            }
        ],
    )
    assert result.remaining_quantity.iloc[0] == 1
    assert result.average_fill_price.iloc[0] == 99
    assert reconcile_orders([order], []).status.iloc[0] == "unknown"


def test_excel_timestamp_roundtrip(tmp_path):
    pytest.importorskip("openpyxl")
    data = pd.DataFrame({"price": [100.0]}, index=pd.date_range("2024-01-01", periods=1, tz="UTC"))
    path = export_table(data, tmp_path / "prices.xlsx")
    loaded = pd.read_excel(path, index_col=0)
    assert loaded.price.iloc[0] == 100 and "+00:00" in loaded.index[0]
