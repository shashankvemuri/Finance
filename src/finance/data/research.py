"""Batch acquisition, public calendars and timestamped snapshot comparisons."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from urllib.parse import urlencode

import pandas as pd

from finance.data.providers import ProviderError
from finance.data.web import PublicWeb


@dataclass(frozen=True)
class BatchResult:
    data: dict
    errors: pd.Series

    def table(self) -> pd.DataFrame:
        """One row per successful company snapshot; failures remain in errors."""
        return pd.DataFrame(self.data).T


def fetch_many(tickers: Iterable[str], fetch: Callable) -> BatchResult:
    """Fetch each distinct ticker sequentially using fetch(ticker).

    Successful values remain in result.data; ProviderError messages are indexed by
    failed ticker in result.errors. Other exceptions propagate. Use result.table()
    for company Series snapshots; price histories remain separate DataFrames in data.
    """
    if isinstance(tickers, str):
        raise ValueError("provide a sequence of tickers")
    data, errors = {}, {}
    for ticker in dict.fromkeys(tickers):
        try:
            data[ticker] = fetch(ticker)
        except ProviderError as exc:
            errors[ticker] = str(exc)
    return BatchResult(data, pd.Series(errors, dtype=str, name="error"))


def snapshot_changes(before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
    """Changes between observations; does not infer when the underlying event occurred."""
    if not before.index.is_unique or not after.index.is_unique:
        raise ValueError("snapshot row keys must be unique")
    rows = []
    for key in before.index.union(after.index):
        for column in before.columns.union(after.columns):
            old = before.at[key, column] if key in before.index and column in before else None
            new = after.at[key, column] if key in after.index and column in after else None
            if (pd.isna(old) and pd.isna(new)) or (pd.notna(old) and pd.notna(new) and old == new):
                continue
            rows.append({"key": key, "field": column, "before": old, "after": new})
    return pd.DataFrame(rows, columns=["key", "field", "before", "after"])


def earnings_calendar(start: str, end: str, *, web: PublicWeb | None = None) -> pd.DataFrame:
    """Nasdaq calendar, start inclusive/end exclusive, at most 31 days per request."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start >= end or end - start > pd.Timedelta(days=31):
        raise ValueError("provide a date range of 1–31 days")
    web = web or PublicWeb()
    rows = []
    for day in pd.date_range(start, end, inclusive="left"):
        payload = web.json(
            "https://api.nasdaq.com/api/calendar/earnings?"
            + urlencode({"date": day.strftime("%Y-%m-%d")})
        )
        data = payload.get("data")
        if not isinstance(data, dict) or "rows" not in data:
            raise ProviderError(f"Nasdaq earnings calendar unavailable for {day.date()}")
        for row in data["rows"] or []:
            if not {"symbol", "name", "epsForecast", "fiscalQuarterEnding"} <= row.keys():
                raise ProviderError("Nasdaq earnings schema changed")
            rows.append(
                {
                    "date": day,
                    "ticker": row["symbol"],
                    "name": row["name"],
                    "session": row.get("time"),
                    "eps_estimate": row["epsForecast"],
                    "quarter_end": row["fiscalQuarterEnding"],
                }
            )
    result = pd.DataFrame(
        rows, columns=["date", "ticker", "name", "session", "eps_estimate", "quarter_end"]
    )
    result["eps_estimate"] = pd.to_numeric(
        result.eps_estimate.astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
        .replace({"N/A": None, "--": None}),
        errors="raise",
    )
    result.attrs.update(source="Nasdaq", retrieved_at=pd.Timestamp.now(tz="UTC").isoformat())
    return result
