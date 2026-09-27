"""Optional daily stock-sentiment data from the Adanos API."""

import json
import math
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import pandas as pd

from finance.data.providers import ProviderError

_SOURCES = {"reddit", "x", "news", "polymarket"}
_METRICS = ["sentiment_score", "buzz_score", "bullish_pct", "bearish_pct"]


def adanos_sentiment(
    ticker: str,
    start: str,
    end: str,
    *,
    source: str = "reddit",
    api_key: str | None = None,
    timeout: float = 15,
) -> pd.DataFrame:
    """Return daily sentiment for inclusive UTC dates, indexed by UTC date.

    Scores retain Adanos units; ``mentions`` counts attributed mentions, while
    Polymarket ``trade_count`` counts trades. An empty frame means the supported
    ticker has no qualifying data in the requested period, not neutral sentiment.
    """
    if source not in _SOURCES:
        raise ValueError(f"source must be one of {', '.join(sorted(_SOURCES))}")
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("ticker must be a nonempty string")
    try:
        first, last = pd.Timestamp(start), pd.Timestamp(end)
    except (TypeError, ValueError) as exc:
        raise ValueError("start and end must be YYYY-MM-DD dates") from exc
    if first.strftime("%Y-%m-%d") != start or last.strftime("%Y-%m-%d") != end or first > last:
        raise ValueError("start and end must be ordered YYYY-MM-DD dates")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive")
    key = os.getenv("ADANOS_API_KEY") if api_key is None else api_key
    if not key or not key.strip():
        raise ValueError("Adanos requires an API key; set ADANOS_API_KEY or pass api_key")

    symbol = ticker.strip().upper().removeprefix("$")
    url = f"https://api.adanos.org/{source}/stocks/v1/stock/{quote(symbol, safe='')}?" + urlencode(
        {"from": start, "to": end}
    )
    request = Request(url, headers={"X-API-Key": key.strip(), "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise ProviderError(f"Adanos {source} request failed (HTTP {exc.code})") from exc
    except (URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProviderError(f"Adanos {source} request failed") from exc

    columns = [*_METRICS, "trade_count" if source == "polymarket" else "mentions"]
    if not isinstance(payload, dict) or not isinstance(payload.get("found"), bool):
        raise ProviderError("Adanos response is missing found status")
    rows = payload.get("daily_trend")
    if rows is None:
        rows = []
    if not isinstance(rows, list):
        raise ProviderError("Adanos daily_trend must be a list")
    if not payload["found"]:
        rows = []
    if not rows:
        return pd.DataFrame(columns=columns, index=pd.DatetimeIndex([], tz="UTC", name="date"))
    try:
        frame = pd.DataFrame(rows)
        if columns[-1] not in frame:
            raise KeyError(columns[-1])
        frame = frame.set_index(pd.to_datetime(frame.pop("date"), format="%Y-%m-%d", utc=True))
        frame.index.name = "date"
        frame = frame.reindex(columns=columns).apply(pd.to_numeric, errors="raise").sort_index()
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderError("Adanos daily_trend schema changed") from exc
    if frame.index.has_duplicates:
        raise ProviderError("Adanos daily_trend has duplicate dates")
    return frame
