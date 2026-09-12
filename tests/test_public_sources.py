import json
from io import BytesIO

import pandas as pd
import pytest

from finance.data import (
    Finviz,
    ProviderError,
    TradingView,
    article_text,
    earnings_calendar,
    fetch_many,
    snapshot_changes,
)
from finance.data.finviz import number
from finance.data.web import PublicWeb


@pytest.mark.parametrize(
    "text,expected", [("1.25B", 1.25e9), ("-2.5%", -0.025), ("$1,020", 1020), ("0", 0)]
)
def test_public_numbers(text, expected):
    assert number(text) == expected


def test_missing_number_is_not_zero():
    assert pd.isna(number("-"))
    with pytest.raises(ProviderError):
        number("login required")


def screen_page(symbols, total=21):
    headers = [
        "No.",
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change %",
        "Volume",
    ]
    rows = ["<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"]
    for symbol in symbols:
        cells = [
            "1",
            f'<a href="quote.ashx?t={symbol}">{symbol}</a>',
            "Company",
            "Tech",
            "Software",
            "USA",
            "1B",
            "10",
            "100",
            "1%",
            "1000",
        ]
        rows.append("<tr>" + "".join(f"<td>{v}</td>" for v in cells) + "</tr>")
    return f"<html><p>#1 / {total} Total</p><table>" + "".join(rows) + "</table></html>"


def test_pagination_completeness_and_schema():
    pytest.importorskip("lxml")

    class Web:
        def text(self, url):
            return screen_page(["LAST"] if "r=21" in url else [f"A{i}" for i in range(20)])

    f = Finviz(Web())
    result = f.screen(limit=21)
    assert len(result) == 21 and result.attrs["complete"]
    limited = f.screen(limit=10)
    assert len(limited) == 10 and not limited.attrs["complete"]

    class Broken:
        def text(self, url):
            return "<html>please log in</html>"

    with pytest.raises(ProviderError):
        Finviz(Broken()).screen()


@pytest.mark.parametrize("missing_offset", [1, 21])
def test_pagination_requires_total_on_every_page(missing_offset):
    pytest.importorskip("lxml")

    class Web:
        def __init__(self):
            self.offsets = []

        def text(self, url):
            offset = 21 if "r=21" in url else 1
            self.offsets.append(offset)
            body = screen_page(["LAST"] if offset == 21 else [f"A{i}" for i in range(20)])
            if offset == missing_offset:
                return body.replace("<p>#1 / 21 Total</p>", "")
            return body

    web = Web()
    with pytest.raises(ProviderError, match="total count missing"):
        Finviz(web).universe("sp500", limit=21)
    assert web.offsets == ([1] if missing_offset == 1 else [1, 21])


def test_explicit_zero_total_is_complete():
    pytest.importorskip("lxml")

    class Web:
        def text(self, url):
            return screen_page([], total=0)

    result = Finviz(Web()).screen()
    assert result.empty and result.attrs["complete"]
    assert result.attrs["total_matches"] == 0
    assert result.index.name == "ticker" and "price" in result


def test_duplicate_pages_fail():
    pytest.importorskip("lxml")

    class Web:
        def text(self, url):
            return screen_page([f"A{i}" for i in range(20)], 40)

    with pytest.raises(ProviderError, match="Duplicate"):
        Finviz(Web()).screen(limit=40)


def test_company_percent_amount_and_missing():
    pytest.importorskip("lxml")
    pairs = [
        ("Market Cap", "1B"),
        ("Price", "100"),
        ("P/E", "-"),
        ("ROE", "20%"),
        ("EPS next Y", "5"),
        ("EPS next Y", "10%"),
    ]
    body = (
        '<table class="snapshot-table2">'
        + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in pairs)
        + "</table>"
    )

    class Web:
        def text(self, url):
            return body

    result = Finviz(Web()).company("A")
    assert result.expected_eps == 5 and result.expected_earnings_growth == 0.1
    assert pd.isna(result.pe)
    assert len(result.attrs["raw_fields"]["EPS next Y"]) == 2


def test_calendar_negative_eps():
    class Web:
        def json(self, url):
            return {
                "data": {
                    "rows": [
                        {
                            "symbol": "A",
                            "name": "A",
                            "epsForecast": "(0.31)",
                            "fiscalQuarterEnding": "Jun/2026",
                        }
                    ]
                }
            }

    result = earnings_calendar("2026-09-04", "2026-09-05", web=Web())
    assert result.eps_estimate.iloc[0] == -0.31


def test_batch_errors_and_changes():
    def fetch(ticker):
        if ticker == "BAD":
            raise ProviderError("unavailable")
        return pd.Series({"price": 10})

    batch = fetch_many(["A", "BAD", "A"], fetch)
    assert list(batch.data) == ["A"] and list(batch.errors.index) == ["BAD"]
    changes = snapshot_changes(batch.table(), pd.DataFrame({"price": [12]}, index=["A"]))
    assert changes.iloc[0].before == 10 and changes.iloc[0].after == 12


def test_cache_and_http_failure(monkeypatch):
    import finance.data.web as module

    calls = []

    def get(*args, **kwargs):
        calls.append(args)
        return BytesIO(b"hello")

    monkeypatch.setattr(module, "urlopen", get)
    web = PublicWeb(interval=0)
    assert web.text("https://example.com") == web.text("https://example.com") == "hello"
    assert len(calls) == 1


def test_vendor_recommendation_schema(monkeypatch):
    import finance.data.tradingview as module

    monkeypatch.setattr(
        module,
        "urlopen",
        lambda *a, **k: BytesIO(
            json.dumps({"data": [{"s": "NASDAQ:AAPL", "d": [100, 0.2, 0.4, 0]}]}).encode()
        ),
    )
    result = TradingView().recommendations(["NASDAQ:AAPL"])
    assert result.overall.iloc[0] == 0.2
    with pytest.raises(ProviderError):
        TradingView().recommendations(["NASDAQ:MSFT"])


def test_transcript_body_excludes_related_cards():
    pytest.importorskip("lxml")

    class Web:
        def text(self, url):
            return (
                '<article><p>Related story</p></article><div id="article-body-transcript"><p>'
                + ("Revenue rose. " * 30)
                + "</p></div>"
            )

    text = article_text("https://www.fool.com/example", web=Web())
    assert "Related" not in text and "Revenue rose." in text
