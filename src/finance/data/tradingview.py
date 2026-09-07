"""Public scanner snapshots, an undocumented provider interface subject to change."""

import json
import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from finance.data.providers import ProviderError


@dataclass(frozen=True)
class TradingView:
    timeout: float = 20

    def recommendations(self, symbols: list[str], interval: str = "1d") -> pd.DataFrame:
        """Exchange-qualified symbols; vendor numeric recommendations in [-1,1], current snapshots."""
        suffixes = {
            "1m": "|1",
            "5m": "|5",
            "15m": "|15",
            "1h": "|60",
            "4h": "|240",
            "1d": "",
            "1w": "|1W",
            "1mo": "|1M",
        }
        if (
            interval not in suffixes
            or not symbols
            or len(symbols) > 100
            or len(set(symbols)) != len(symbols)
        ):
            raise ValueError("supported interval and 1–100 distinct symbols required")
        if self.timeout <= 0 or any(
            not re.fullmatch(r"[A-Z0-9_]+:[A-Z0-9_.!-]+", s) for s in symbols
        ):
            raise ValueError("positive timeout and EXCHANGE:SYMBOL identifiers required")
        columns = [
            name + suffixes[interval]
            for name in ["close", "Recommend.All", "Recommend.MA", "Recommend.Other"]
        ]
        payload = {
            "symbols": {"tickers": symbols, "query": {"types": []}},
            "columns": columns,
            "range": [0, len(symbols)],
        }
        request = Request(
            "https://scanner.tradingview.com/america/scan",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = json.load(response)
            rows = [
                {
                    "symbol": row["s"],
                    **dict(
                        zip(
                            ["price", "overall", "moving_averages", "oscillators"],
                            row["d"],
                            strict=True,
                        )
                    ),
                }
                for row in raw["data"]
            ]
            result = pd.DataFrame(rows).set_index("symbol").reindex(symbols)
            if (
                not np.isfinite(result).all().all()
                or (result.price <= 0).any()
                or (result.drop(columns="price").abs() > 1).any().any()
            ):
                raise ValueError("missing symbols or invalid recommendations")
            result.attrs.update(
                provider="TradingView public scanner",
                interval=interval,
                retrieved_at=pd.Timestamp.now(tz="UTC").isoformat(),
                historical=False,
            )
            return result
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
            raise ProviderError(f"TradingView scanner failed: {exc}") from exc
