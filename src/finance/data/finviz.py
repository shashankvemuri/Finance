"""Public Finviz snapshots. Percentages are fractions; source symbols are preserved."""

import re
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import numpy as np
import pandas as pd

from finance.data.providers import ProviderError
from finance.data.web import PublicWeb


def number(value: str) -> float:
    value = value.strip().replace(",", "").replace("$", "").replace("−", "-")
    if value in ("", "-", "--", "N/A", "None"):
        return np.nan
    scale = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12, "%": 0.01}
    factor = scale.get(value[-1], 1)
    if value[-1] in scale:
        value = value[:-1]
    try:
        result = float(value) * factor
        if not np.isfinite(result):
            raise ValueError("nonfinite number")
        return result
    except ValueError as exc:
        raise ProviderError(f"Unexpected numeric field: {value!r}") from exc


def _root(body):
    from lxml import html

    return html.fromstring(body)


def _text(node):
    return " ".join(node.text_content().split())


def _symbol(cell):
    for link in cell.xpath(".//a[@href]"):
        query = parse_qs(urlparse(link.get("href")).query)
        if "t" in query:
            return query["t"][0]
    raise ProviderError("Ticker link missing from Finviz row")


def _table(root, required):
    for table in root.xpath("//table"):
        rows = table.xpath("./tr|./thead/tr|./tbody/tr")
        if not rows:
            continue
        headers = [_text(cell) for cell in rows[0].xpath("./td|./th")]
        if set(required) <= set(headers):
            return headers, rows[1:]
    raise ProviderError(f"Finviz table missing columns {required}")


def _stamp(result, url):
    result.attrs.update(
        source=url, retrieved_at=pd.Timestamp.now(tz="UTC").isoformat(), historical=False
    )
    return result


@dataclass
class Finviz:
    """Public snapshots requiring the data extra; attrs record source and retrieval time."""

    web: PublicWeb = field(default_factory=PublicWeb)

    def _get(self, path, **params):
        url = "https://finviz.com/" + path + ("?" + urlencode(params) if params else "")
        return _root(self.web.text(url)), url

    def screen(
        self, filters: list[str] | None = None, *, order: str = "ticker", limit: int = 100
    ) -> pd.DataFrame:
        """Fetch up to limit rows using Finviz filter codes, e.g. ['cap_largeover'].

        Index: source ticker. Columns: name, sector, industry, country, market_cap,
        pe, price, change, volume. Percent change is fractional; missing numbers are NaN.
        Inspect attrs['complete'] and attrs['total_matches'] before treating this as
        the full result. These are current snapshots, not historical constituents.
        """
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10000:
            raise ValueError("limit must be an integer in [1,10000]")
        if any(not re.fullmatch(r"[\w.-]+", item) for item in [order, *(filters or [])]):
            raise ValueError("invalid Finviz filter/order code")
        records, total = [], None
        url = ""
        for offset in range(1, limit + 1, 20):
            root, url = self._get(
                "screener.ashx", v=111, f=",".join(filters or []), o=order, r=offset
            )
            text = _text(root)
            match = re.search(r"/\s*([\d,]+)\s+Total", text)
            if match is None:
                raise ProviderError(
                    f"Finviz total count missing at offset {offset}; completeness cannot be established"
                )
            count = int(match[1].replace(",", ""))
            if total is not None and count != total:
                raise ProviderError("Screener changed during pagination; retry the snapshot")
            total = count
            if total == 0:
                break
            headers, rows = _table(root, ["Ticker", "Company", "Market Cap", "Price"])
            page = []
            for row in rows:
                cells = row.xpath("./td")
                if len(cells) != len(headers):
                    continue
                values = dict(zip(headers, cells, strict=True))
                page.append(
                    {
                        "ticker": _symbol(values["Ticker"]),
                        "name": _text(values["Company"]),
                        "sector": _text(values["Sector"]),
                        "industry": _text(values["Industry"]),
                        "country": _text(values["Country"]),
                        "market_cap": number(_text(values["Market Cap"])),
                        "pe": number(_text(values["P/E"])),
                        "price": number(_text(values["Price"])),
                        "change": number(_text(values["Change %"])),
                        "volume": number(_text(values["Volume"])),
                    }
                )
            if not page:
                raise ProviderError("Finviz returned no parseable screener rows")
            records.extend(page)
            if len(records) >= total:
                break
        result = pd.DataFrame(
            records,
            columns=[
                "ticker",
                "name",
                "sector",
                "industry",
                "country",
                "market_cap",
                "pe",
                "price",
                "change",
                "volume",
            ],
        ).set_index("ticker")
        if result.index.has_duplicates:
            raise ProviderError("Duplicate tickers across screener pages; retry the snapshot")
        result = result.iloc[:limit]
        result.attrs.update(
            total_matches=total, complete=len(result) == total, filters=filters or []
        )
        return _stamp(result, url)

    def universe(self, index: str, *, limit: int = 3000) -> pd.DataFrame:
        """Return screen rows for sp500, dow, nasdaq100 or russell2000.

        Membership follows Finviz's current classification. The index contains tickers;
        attrs['complete'] reports whether all provider matches fit within limit.
        """
        codes = {"sp500": "sp500", "dow": "dji", "nasdaq100": "ndx", "russell2000": "rut"}
        if index not in codes:
            raise ValueError(f"index must be one of {list(codes)}")
        return self.screen([f"idx_{codes[index]}"], limit=limit)

    def company(self, ticker: str) -> pd.Series:
        """Numeric snapshot named by ticker; growth, yield and ownership are fractions.

        RSI uses 0–100. Unavailable numbers are NaN; source-absent optional fields may
        be omitted. attrs['raw_fields'] retains source labels and duplicate values.
        """
        root, url = self._get("quote.ashx", t=ticker)
        fields = {
            "Market Cap": "market_cap",
            "Enterprise Value": "enterprise_value",
            "P/E": "pe",
            "Forward P/E": "forward_pe",
            "PEG": "peg",
            "P/S": "price_sales",
            "P/B": "price_book",
            "P/FCF": "price_fcf",
            "ROE": "roe",
            "ROA": "roa",
            "ROIC": "roic",
            "Gross Margin": "gross_margin",
            "Oper. Margin": "operating_margin",
            "Profit Margin": "profit_margin",
            "EPS Q/Q": "earnings_growth",
            "Sales Q/Q": "revenue_growth",
            "EPS Y/Y TTM": "earnings_growth_ttm",
            "Sales Y/Y TTM": "revenue_growth_ttm",
            "EPS next 5Y": "expected_earnings_growth_5y",
            "Insider Own": "insider_ownership",
            "Insider Trans": "insider_transactions",
            "Inst Own": "institutional_ownership",
            "Inst Trans": "institutional_transactions",
            "SMA20": "distance_sma20",
            "SMA50": "distance_sma50",
            "SMA200": "distance_sma200",
            "RSI (14)": "rsi",
            "Rel Volume": "relative_volume",
            "Avg Volume": "average_volume",
            "Volume": "volume",
            "Price": "price",
            "Target Price": "target_price",
            "Recom": "analyst_rating",
            "Shs Outstand": "shares",
            "Short Float": "short_float",
            "Beta": "beta",
            "Debt/Eq": "debt_equity",
            "Perf Year": "return_1y",
            "Perf Quarter": "return_quarter",
            "Perf Month": "return_month",
        }
        result, raw = {}, {}
        for row in root.xpath('//table[contains(@class,"snapshot-table2")]//tr'):
            cells = row.xpath("./td")
            for i in range(0, len(cells) - 1, 2):
                label, value = _text(cells[i]), _text(cells[i + 1])
                # Some source labels are duplicated (EPS next Y amount versus growth).
                raw.setdefault(label, []).append(value)
                if label in fields:
                    result[fields[label]] = number(value)
                if label == "EPS next Y":
                    result["expected_earnings_growth" if "%" in value else "expected_eps"] = number(
                        value
                    )
                if label in ("52W High", "52W Low"):
                    parts = value.split()
                    if len(parts) == 2:
                        suffix = "high" if label.endswith("High") else "low"
                        result[f"{suffix}_52w"] = number(parts[0])
                        result[f"distance_{suffix}_52w"] = number(parts[1])
                if label == "Dividend TTM":
                    match = re.fullmatch(r"([\d.,]+)\s*\(([\d.]+%)\)", value)
                    if match:
                        result["annual_dividend"], result["dividend_yield"] = (
                            number(match[1]),
                            number(match[2]),
                        )
        if not {"price", "market_cap", "pe", "roe"} <= result.keys():
            raise ProviderError(f"Finviz company schema missing for {ticker}")
        if not np.isfinite(result["price"]) or result["price"] <= 0:
            raise ProviderError(f"Invalid Finviz price for {ticker}")
        output = pd.Series(result, name=ticker)
        output.attrs["raw_fields"] = raw
        return _stamp(output, url)

    def analysts(self, ticker: str) -> pd.DataFrame:
        """Rows of date, action, analyst, rating_change and target_change.

        Dates are timezone-naive; rating and target changes retain provider text.
        """
        root, url = self._get("quote.ashx", t=ticker)
        headers, rows = _table(
            root, ["Date", "Action", "Analyst", "Rating Change", "Price Target Change"]
        )
        values = [[_text(c) for c in row.xpath("./td")] for row in rows]
        result = pd.DataFrame([v for v in values if len(v) == len(headers)], columns=headers)
        result.columns = ["date", "action", "analyst", "rating_change", "target_change"]
        result["date"] = pd.to_datetime(result.date, format="%b-%d-%y", errors="raise")
        return _stamp(result, url)

    def insiders(self) -> pd.DataFrame:
        """Recent market-wide transactions, not a complete filing history.

        Columns: ticker, owner, relationship, date, transaction, price, shares, value,
        filing. date is the transaction date; filing retains the source display text.
        """
        root, url = self._get("insidertrading.ashx")
        headers, rows = _table(
            root, ["Ticker", "Owner", "Transaction", "Cost", "#Shares", "Value ($)"]
        )
        records = []
        for row in rows:
            cells = row.xpath("./td")
            if len(cells) != len(headers):
                continue
            values = dict(zip(headers, cells, strict=True))
            records.append(
                {
                    "ticker": _symbol(values["Ticker"]),
                    "owner": _text(values["Owner"]),
                    "relationship": _text(values["Relationship"]),
                    "date": _text(values["Date"]),
                    "transaction": _text(values["Transaction"]),
                    "price": number(_text(values["Cost"])),
                    "shares": number(_text(values["#Shares"])),
                    "value": number(_text(values["Value ($)"])),
                    "filing": _text(values["SEC Form 4"]),
                }
            )
        if not records:
            raise ProviderError("No insider rows parsed")
        result = pd.DataFrame(records)
        result["date"] = pd.to_datetime(result.date, format="%b %d '%y", errors="raise")
        return _stamp(result, url)

    def news(self, ticker: str | None = None) -> pd.DataFrame:
        """Company or market headlines: ticker, title, url and source_time columns.

        source_time retains display text, not a normalized publication timestamp.
        Rows are deduplicated by URL; article bodies are not included.
        """
        root, url = self._get("quote.ashx", t=ticker) if ticker else self._get("news.ashx")
        selector = (
            '//table[@id="news-table"]//tr'
            if ticker
            else '//table[contains(@class,"styled-table-new")]//tr'
        )
        records = []
        for row in root.xpath(selector):
            links = row.xpath('.//a[starts-with(@href,"http")]')
            if not links:
                continue
            link = max(links, key=lambda a: len(_text(a)))
            if not _text(link):
                continue
            records.append(
                {
                    "ticker": ticker,
                    "title": _text(link),
                    "url": urljoin(url, link.get("href")),
                    "source_time": next(
                        (
                            m.group()
                            for m in [
                                re.search(
                                    r"(?:[A-Z][a-z]{2}-\d{2}-\d{2} |Today )?\d{2}:\d{2}[AP]M",
                                    _text(row),
                                )
                            ]
                            if m
                        ),
                        "",
                    ),
                }
            )
        if not records:
            raise ProviderError("No news stories parsed")
        return _stamp(pd.DataFrame(records).drop_duplicates("url").reset_index(drop=True), url)

    def market(self) -> dict[str, pd.DataFrame]:
        """Homepage movers, macro releases, futures and FX snapshots. Source time/units retained."""
        root, url = self._get("")
        result = {}
        for name, required in [
            ("movers", ["Ticker", "Last", "Change %", "Volume", "", "Signal"]),
            (
                "economy",
                ["Date", "Time", "Impact", "Release", "For", "Actual", "Expected", "Prior"],
            ),
            ("futures", ["Futures", "Last", "Change", "Change %"]),
            ("forex", ["Forex & Bonds", "Last", "Change", "Change %"]),
        ]:
            tables = []
            for table in root.xpath("//table"):
                rows = table.xpath("./tr|./thead/tr|./tbody/tr")
                if not rows:
                    continue
                headers = [_text(c) for c in rows[0].xpath("./td|./th")]
                if headers != required:
                    continue
                values = []
                for row in rows[1:]:
                    cells = row.xpath("./td")
                    if len(cells) == len(headers):
                        values.append(
                            [
                                _symbol(cells[0]) if name == "movers" else _text(cells[0]),
                                *[_text(c) for c in cells[1:]],
                            ]
                        )
                tables.append(pd.DataFrame(values, columns=headers))
            if not tables:
                raise ProviderError(f"Finviz {name} table missing")
            result[name] = _stamp(
                pd.concat(tables, ignore_index=True).drop(columns=[""], errors="ignore"), url
            )
        return result
