import json
from io import BytesIO

import pandas as pd
import pytest

import finance.data.providers as providers
from finance.data import (
    ProviderError,
    YahooFinance,
    close_matrix,
    cot_financial_futures,
    dividend_calendar,
    exchange_universe,
    sp500_constituents,
)


def test_exchange_na_is_a_symbol(monkeypatch):
    nasdaq = "Symbol|Security Name|Test Issue|ETF\nNA|Nano Labs|N|N\nTEST|Test|Y|N\nFile Creation Time: foo|||\n"
    other = "ACT Symbol|Security Name|Test Issue|ETF|Exchange\nABC|ABC Corp|N|N|N\n"
    monkeypatch.setattr(
        providers, "fetch_text", lambda url, **kw: nasdaq if "nasdaqlisted" in url else other
    )
    result = exchange_universe()
    assert "NA" in result.index
    assert "TEST" not in result.index
    assert len(result) == 2


def test_bad_provider_schema_fails_explicitly(monkeypatch, ohlcv):
    class FakeTicker:
        def history(self, **kwargs):
            return pd.DataFrame()

        def get_info(self):
            return {}

        def get_earnings_dates(self):
            return pd.DataFrame({"surprise": [1]})

        def get_news(self):
            return []

    monkeypatch.setattr(YahooFinance, "_ticker", lambda *a: FakeTicker())
    provider = YahooFinance()
    for fn in [
        lambda: provider.history("AAPL", "2023-01-01", "2024-01-01"),
        lambda: provider.company("AAPL"),
        lambda: provider.earnings("AAPL"),
        lambda: provider.news("AAPL"),
        lambda: provider.dividends("AAPL", "2023-01-01", "2024-01-01"),
    ]:
        with pytest.raises(ProviderError):
            fn()
    with pytest.raises(ValueError):
        provider.history("AAPL", "2024-01-01", "2023-01-01")
    aligned = close_matrix({"a": ohlcv, "b": ohlcv.iloc[1:]})
    assert len(aligned) == len(ohlcv) - 1


def test_calendar_and_cot_normalization(monkeypatch):
    row = {
        "symbol": "AAPL",
        "companyName": "Apple",
        "dividend_Ex_Date": "09/04/2026",
        "payment_Date": "09/20/2026",
        "record_Date": "09/05/2026",
        "dividend_Rate": "$0.26",
        "indicated_Annual_Dividend": "1.04",
    }
    monkeypatch.setattr(
        providers,
        "urlopen",
        lambda *a, **k: BytesIO(json.dumps({"data": {"calendar": {"rows": [row]}}}).encode()),
    )
    result = dividend_calendar("2026-09-04")
    assert result.dividend.iloc[0] == 0.26
    assert result.annual_dividend.iloc[0] == 1.04
    assert result.ex_date.iloc[0] == pd.Timestamp("2026-09-04")
    cot = [
        {
            "report_date_as_yyyy_mm_dd": "2023-01-03",
            "open_interest_all": "100",
            "dealer_positions_long_all": "20",
            "dealer_positions_short_all": "15",
            "lev_money_positions_long": "40",
            "lev_money_positions_short": "20",
        }
    ]
    monkeypatch.setattr(providers, "fetch_text", lambda *a, **k: json.dumps(cot))
    result = cot_financial_futures("13874A", "2023-01-01", "2024-01-01")
    assert result.open_interest_all.iloc[0] == 100
    with pytest.raises(ValueError):
        cot_financial_futures("' OR 1=1", "2023-01-01", "2024-01-01")


def test_sp500_schema_validation(monkeypatch):
    pytest.importorskip("lxml")
    monkeypatch.setattr(
        providers,
        "fetch_text",
        lambda *a, **k: "<table><tr><th>foo</th></tr><tr><td>bar</td></tr></table>",
    )
    with pytest.raises(ProviderError):
        sp500_constituents()


def test_calendar_accepts_numeric_amounts(monkeypatch):
    row = {
        "symbol": "AAPL",
        "companyName": "Apple",
        "dividend_Ex_Date": "09/04/2026",
        "payment_Date": "09/20/2026",
        "record_Date": "09/05/2026",
        "dividend_Rate": 0.26,
        "indicated_Annual_Dividend": 1.04,
    }
    monkeypatch.setattr(
        providers,
        "urlopen",
        lambda *a, **k: BytesIO(json.dumps({"data": {"calendar": {"rows": [row]}}}).encode()),
    )
    assert dividend_calendar("2026-09-04").dividend.iloc[0] == 0.26
