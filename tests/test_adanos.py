import json
from io import BytesIO
from urllib.error import HTTPError

import pandas as pd
import pytest

import finance.data.adanos as adanos
from finance.data import ProviderError, adanos_sentiment


def test_adanos_sentiment_uses_explicit_utc_window_and_key(monkeypatch):
    calls = []

    def fake_open(request, *, timeout):
        calls.append((request, timeout))
        return BytesIO(
            json.dumps(
                {
                    "found": True,
                    "daily_trend": [
                        {
                            "date": "2026-09-02",
                            "mentions": 4,
                            "sentiment_score": 0.25,
                            "buzz_score": 30,
                            "bullish_pct": 50,
                            "bearish_pct": 25,
                        },
                        {
                            "date": "2026-09-01",
                            "mentions": 2,
                            "sentiment_score": -0.1,
                            "buzz_score": 10,
                            "bullish_pct": 20,
                            "bearish_pct": 40,
                        },
                    ],
                }
            ).encode()
        )

    monkeypatch.setattr(adanos, "urlopen", fake_open)
    result = adanos_sentiment("$AAPL", "2026-09-01", "2026-09-02", source="x", api_key="test-key")
    assert result.index.equals(pd.date_range("2026-09-01", periods=2, tz="UTC", name="date"))
    assert result.mentions.tolist() == [2, 4]
    assert result.sentiment_score.tolist() == [-0.1, 0.25]
    request, timeout = calls.pop()
    assert request.full_url == (
        "https://api.adanos.org/x/stocks/v1/stock/AAPL?from=2026-09-01&to=2026-09-02"
    )
    assert request.get_header("X-api-key") == "test-key"
    assert timeout == 15


def test_adanos_polymarket_activity_and_empty_period(monkeypatch):
    monkeypatch.setenv("ADANOS_API_KEY", "test-key")
    payload = {
        "found": True,
        "daily_trend": [
            {
                "date": "2026-09-01",
                "trade_count": 8,
                "sentiment_score": 0.2,
                "buzz_score": 45,
                "bullish_pct": 60,
                "bearish_pct": 20,
            }
        ],
    }
    monkeypatch.setattr(adanos, "urlopen", lambda *a, **k: BytesIO(json.dumps(payload).encode()))
    frame = adanos_sentiment("AAPL", "2026-09-01", "2026-09-01", source="polymarket")
    assert frame.trade_count.iloc[0] == 8
    assert "mentions" not in frame
    payload["found"] = False
    payload["daily_trend"] = None
    empty = adanos_sentiment("AAPL", "2026-09-01", "2026-09-01", source="polymarket")
    assert empty.empty and empty.index.tz is not None
    assert empty.columns.tolist() == frame.columns.tolist()


@pytest.mark.parametrize("source", ["reddit", "news"])
def test_adanos_other_stock_sources(monkeypatch, source):
    monkeypatch.setattr(
        adanos,
        "urlopen",
        lambda *a, **k: BytesIO(json.dumps({"found": False, "daily_trend": []}).encode()),
    )
    result = adanos_sentiment("TSLA", "2026-09-01", "2026-09-02", source=source, api_key="key")
    assert result.empty


def test_adanos_invalid_inputs_do_not_make_requests(monkeypatch):
    monkeypatch.setattr(adanos, "urlopen", lambda *a, **k: pytest.fail("unexpected request"))
    for kwargs in [
        {"source": "crypto"},
        {"source": "reddit", "timeout": 0},
    ]:
        with pytest.raises(ValueError):
            adanos_sentiment("AAPL", "2026-09-01", "2026-09-02", api_key="key", **kwargs)
    with pytest.raises(ValueError):
        adanos_sentiment("AAPL", "2026-09-02", "2026-09-01", api_key="key")
    with pytest.raises(ValueError):
        adanos_sentiment("AAPL", "2026-09-01", "2026-09-02", api_key="")


def test_adanos_http_error_does_not_expose_key(monkeypatch):
    def fake_open(request, *, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(adanos, "urlopen", fake_open)
    with pytest.raises(ProviderError, match="HTTP 403") as error:
        adanos_sentiment("AAPL", "2026-09-01", "2026-09-02", api_key="private-test-key")
    assert "private-test-key" not in str(error.value)


def test_adanos_rejects_broken_daily_schema(monkeypatch):
    monkeypatch.setattr(
        adanos,
        "urlopen",
        lambda *a, **k: BytesIO(
            json.dumps({"found": True, "daily_trend": [{"date": "bad"}]}).encode()
        ),
    )
    with pytest.raises(ProviderError, match="schema changed"):
        adanos_sentiment("AAPL", "2026-09-01", "2026-09-02", api_key="key")


def test_adanos_accepts_optional_daily_metrics(monkeypatch):
    monkeypatch.setattr(
        adanos,
        "urlopen",
        lambda *a, **k: BytesIO(
            json.dumps(
                {"found": True, "daily_trend": [{"date": "2026-09-01", "mentions": 3}]}
            ).encode()
        ),
    )
    result = adanos_sentiment("AAPL", "2026-09-01", "2026-09-01", api_key="key")
    assert result.mentions.iloc[0] == 3
    assert pd.isna(result.sentiment_score.iloc[0])
