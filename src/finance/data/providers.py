from dataclasses import dataclass
from io import StringIO
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

from finance.data.normalize import normalize_ohlcv, normalize_ticker


class ProviderError(RuntimeError):
    """Provider unavailable, missing data, or unexpected schema."""


class PriceProvider(Protocol):
    def history(
        self, ticker: str, start: str, end: str, *, interval: str = "1d"
    ) -> pd.DataFrame: ...


def fetch_text(url: str, *, timeout: float = 15) -> str:
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    request = Request(url, headers={"User-Agent": "FinanceToolkit research"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError, UnicodeError) as exc:
        raise ProviderError(f"Unable to retrieve {url}: {exc}") from exc


@dataclass(frozen=True)
class YahooFinance:
    """Optional Yahoo adapter. End is exclusive; adjusted OHLC includes splits/dividends."""

    timeout: float = 15
    adjusted: bool = True

    def _ticker(self, ticker: str):
        import yfinance as yf
        from curl_cffi.requests import Session

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        return yf.Ticker(
            normalize_ticker(ticker), session=Session(impersonate="chrome", timeout=self.timeout)
        )

    def history(self, ticker: str, start: str, end: str, *, interval: str = "1d") -> pd.DataFrame:
        """Return float open/high/low/close/volume columns for [start, end).

        The sorted, unique DatetimeIndex retains the provider timezone. Missing or
        invalid OHLCV raises ProviderError. attrs['adjusted'] records the price basis;
        the default includes split and dividend adjustments in all OHLC prices.
        """
        if pd.Timestamp(start) >= pd.Timestamp(end):
            raise ValueError("start must precede end")
        handle = self._ticker(ticker)
        try:
            raw = handle.history(
                start=start,
                end=end,
                interval=interval,
                auto_adjust=self.adjusted,
                actions=False,
                timeout=self.timeout,
            )
            result = normalize_ohlcv(raw)
        except Exception as exc:
            # The optional provider has several transport/parser exception families.
            # Preserve the cause and fail explicitly at this external boundary.
            raise ProviderError(f"Yahoo history failed for {ticker} ({interval}): {exc}") from exc
        result.attrs.update(
            provider="Yahoo Finance", ticker=normalize_ticker(ticker), adjusted=self.adjusted
        )
        return result

    def dividends(self, ticker: str, start: str, end: str) -> pd.Series:
        handle = self._ticker(ticker)
        try:
            raw = handle.history(
                start=start,
                end=end,
                auto_adjust=False,
                actions=True,
                timeout=self.timeout,
            )
            if raw.empty or "Dividends" not in raw:
                raise ValueError("missing dividend history")
            result = pd.to_numeric(raw["Dividends"], errors="raise")
            return result[result != 0].rename("dividend")
        except Exception as exc:
            raise ProviderError(f"Yahoo dividends failed for {ticker}: {exc}") from exc

    def company(self, ticker: str) -> pd.Series:
        """Current snapshot, unsuitable for historical fundamental backtests; rates are fractions."""
        handle = self._ticker(ticker)
        fields = {
            "longName": "name",
            "currentPrice": "price",
            "marketCap": "market_cap",
            "trailingPE": "pe",
            "returnOnEquity": "roe",
            "returnOnAssets": "roa",
            "revenueGrowth": "revenue_growth",
            "earningsGrowth": "earnings_growth",
            "grossMargins": "gross_margin",
            "dividendRate": "annual_dividend",
            "totalDebt": "debt",
            "totalCash": "cash",
            "freeCashflow": "free_cash_flow",
            "sharesOutstanding": "shares",
            "recommendationMean": "analyst_rating",
        }
        try:
            info = handle.get_info()
            if not info or "marketCap" not in info:
                raise ValueError("company snapshot lacks marketCap")
            result = pd.Series(
                {dest: info.get(source) for source, dest in fields.items()},
                name=normalize_ticker(ticker),
            )
            price, dividend = result["price"], result["annual_dividend"]
            result["dividend_yield"] = (
                dividend / price if dividend is not None and price else float("nan")
            )
            return result
        except Exception as exc:
            raise ProviderError(f"Yahoo company failed for {ticker}: {exc}") from exc

    def statements(
        self, ticker: str, kind: str = "income", frequency: str = "annual"
    ) -> pd.DataFrame:
        """Period-end rows, provider statement labels, reported currency units; restatements possible."""
        names = {"income": "income_stmt", "balance": "balance_sheet", "cashflow": "cashflow"}
        if kind not in names or frequency not in ("annual", "quarterly"):
            raise ValueError("kind: income/balance/cashflow; frequency: annual/quarterly")
        handle = self._ticker(ticker)
        attribute = ("quarterly_" if frequency == "quarterly" else "") + names[kind]
        try:
            raw = getattr(handle, attribute)
            if not isinstance(raw, pd.DataFrame) or raw.empty or raw.index.has_duplicates:
                raise ValueError("missing or duplicate statement fields")
            result = raw.T.apply(pd.to_numeric, errors="raise").sort_index().dropna(how="all")
            result.index = pd.DatetimeIndex(result.index, name="period_end")
            result.attrs.update(
                provider="Yahoo Finance",
                ticker=ticker,
                frequency=frequency,
                retrieved_at=pd.Timestamp.now(tz="UTC").isoformat(),
                currency=handle.get_info().get("financialCurrency"),
                restated=True,
            )
            return result
        except Exception as exc:
            raise ProviderError(f"Yahoo {kind} statement failed for {ticker}: {exc}") from exc

    def earnings(self, ticker: str) -> pd.DataFrame:
        return self._table(ticker, "get_earnings_dates", ["EPS Estimate", "Reported EPS"])

    def insider_transactions(self, ticker: str) -> pd.DataFrame:
        return self._table(ticker, "get_insider_transactions", ["Shares", "Start Date"])

    def _table(self, ticker: str, method: str, required: list[str]) -> pd.DataFrame:
        handle = self._ticker(ticker)
        try:
            result = getattr(handle, method)()
            if (
                not isinstance(result, pd.DataFrame)
                or result.empty
                or not set(required) <= set(result)
            ):
                raise ValueError(f"missing table/columns: {required}")
            return result.copy()
        except Exception as exc:
            raise ProviderError(f"Yahoo {method} failed for {ticker}: {exc}") from exc

    def news(self, ticker: str) -> pd.DataFrame:
        handle = self._ticker(ticker)
        try:
            stories = handle.get_news()
            rows = []
            for story in stories:
                content = story.get("content", story)
                rows.append(
                    {
                        "title": content["title"],
                        "published": content.get("pubDate"),
                        "url": content.get("canonicalUrl", {}).get("url", content.get("link")),
                    }
                )
            if not rows:
                raise ValueError("empty news response")
            return pd.DataFrame(rows)
        except Exception as exc:
            raise ProviderError(f"Yahoo news failed for {ticker}: {exc}") from exc


def sp500_constituents(*, timeout: float = 15) -> pd.DataFrame:
    """Current constituents, not a point-in-time universe (survivorship bias). Requires data extra."""
    html = fetch_text("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", timeout=timeout)
    try:
        tables = pd.read_html(StringIO(html))
        table = next(t for t in tables if {"Symbol", "Security", "GICS Sector"} <= set(t))
        result = table[["Symbol", "Security", "GICS Sector"]].copy()
        result.columns = ["ticker", "name", "sector"]
        result["ticker"] = result.ticker.map(normalize_ticker)
        if not 400 <= len(result) <= 600 or result.ticker.duplicated().any():
            raise ValueError("unexpected constituent count or duplicates")
        return result.set_index("ticker")
    except (ValueError, StopIteration, KeyError) as exc:
        raise ProviderError(f"S&P 500 constituent schema changed: {exc}") from exc


def exchange_universe(*, timeout: float = 15) -> pd.DataFrame:
    """Current Nasdaq Trader listings; excludes test issues, retains ETF flag."""
    frames = []
    for filename, symbol_col in [("nasdaqlisted.txt", "Symbol"), ("otherlisted.txt", "ACT Symbol")]:
        body = fetch_text(
            f"https://www.nasdaqtrader.com/dynamic/SymDir/{filename}", timeout=timeout
        )
        table = pd.read_csv(StringIO(body), sep="|", dtype=str, keep_default_na=False)
        required = {symbol_col, "Security Name", "Test Issue", "ETF"}
        if not required <= set(table):
            raise ProviderError(f"Unexpected Nasdaq directory schema: {filename}")
        table = table.loc[table["Test Issue"] == "N"].copy()
        exchange = table["Exchange"] if "Exchange" in table else pd.Series("Q", index=table.index)
        frames.append(
            pd.DataFrame(
                {
                    "ticker": table[symbol_col],
                    "name": table["Security Name"],
                    "exchange": exchange,
                    "etf": table["ETF"].eq("Y"),
                }
            )
        )
    result = pd.concat(frames, ignore_index=True)
    if result.empty or result.ticker.isna().any() or result.ticker.duplicated().any():
        raise ProviderError("empty, missing or duplicate exchange listings")
    # Preserve exchange-native symbols; provider-specific translation is explicit.
    return result.set_index("ticker").sort_index()


def close_matrix(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Intersect trading timestamps explicitly; never forward-fill suspended/missing assets."""
    if not prices:
        raise ValueError("provide at least one asset")
    result = pd.concat(
        {ticker: normalize_ohlcv(data).close for ticker, data in prices.items()}, axis=1
    ).dropna()
    if result.empty:
        raise ValueError("assets have no common observations")
    return result


def dividend_calendar(date: str, *, timeout: float = 15) -> pd.DataFrame:
    """Nasdaq ex-dividend calendar for one date; amounts in provider-reported currency."""
    import json

    day = pd.Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://api.nasdaq.com/api/calendar/dividends?date={day}"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Origin": "https://www.nasdaq.com",
        },
    )
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        calendar = payload["data"]["calendar"]
        if calendar is None:
            raise ValueError("calendar unavailable")
        rows = calendar.get("rows") or []
        columns = {
            "symbol": "ticker",
            "companyName": "company",
            "dividend_Ex_Date": "ex_date",
            "payment_Date": "payment_date",
            "record_Date": "record_date",
            "dividend_Rate": "dividend",
            "indicated_Annual_Dividend": "annual_dividend",
        }
        if not rows:
            return pd.DataFrame(columns=list(columns.values()))
        data = pd.DataFrame(rows)
        if not set(columns) <= set(data):
            raise ValueError(f"unexpected calendar columns: {list(data)}")
        data = data[list(columns)].rename(columns=columns)
        for col in ["dividend", "annual_dividend"]:
            data[col] = pd.to_numeric(
                data[col]
                .astype("string")
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .replace({"N/A": None, "--": None, "": None}),
                errors="raise",
            )
        for col in ["ex_date", "payment_date", "record_date"]:
            data[col] = pd.to_datetime(data[col].replace({"N/A": None, "": None}), errors="raise")
        return data
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        raise ProviderError(f"Nasdaq dividend calendar failed for {day}: {exc}") from exc


def cot_financial_futures(
    contract_code: str, start: str, end: str, *, timeout: float = 15
) -> pd.DataFrame:
    """CFTC TFF futures-only positioning by report date, not publication/availability date."""
    import json
    import re
    from urllib.parse import urlencode

    if not re.fullmatch(r"[A-Za-z0-9]{6}", contract_code):
        raise ValueError("provide a six-character CFTC contract code")
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start >= end:
        raise ValueError("start must precede end")
    query = {
        "$where": f"cftc_contract_market_code='{contract_code}' AND report_date_as_yyyy_mm_dd >= '{start:%Y-%m-%d}T00:00:00' AND report_date_as_yyyy_mm_dd < '{end:%Y-%m-%d}T00:00:00'",
        "$order": "report_date_as_yyyy_mm_dd",
        "$limit": "5000",
    }
    payload = json.loads(
        fetch_text(
            "https://publicreporting.cftc.gov/resource/gpe5-46if.json?" + urlencode(query),
            timeout=timeout,
        )
    )
    data = pd.DataFrame(payload)
    required = {
        "report_date_as_yyyy_mm_dd",
        "open_interest_all",
        "dealer_positions_long_all",
        "dealer_positions_short_all",
        "lev_money_positions_long",
        "lev_money_positions_short",
    }
    if data.empty or not required <= set(data) or len(data) >= 5000:
        raise ProviderError("CFTC returned empty, truncated or malformed positioning data")
    data = data[list(sorted(required))].rename(columns={"report_date_as_yyyy_mm_dd": "report_date"})
    data["report_date"] = pd.to_datetime(data.report_date, errors="raise")
    data = data.set_index("report_date").apply(pd.to_numeric, errors="raise")
    if data.index.duplicated().any() or data.isna().any().any() or (data < 0).any().any():
        raise ProviderError("CFTC report contains invalid positions")
    return data
