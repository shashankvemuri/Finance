"""Bounded public-page retrieval; parsing stays in each provider."""

import json
import math
import time
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from finance.data.providers import ProviderError


@dataclass
class PublicWeb:
    timeout: float = 20
    interval: float = 1
    cache_seconds: float = 300
    _cache: dict = field(default_factory=dict, init=False, repr=False)
    _last_request: float = field(default=0, init=False, repr=False)

    def text(self, url: str) -> str:
        if (
            not all(math.isfinite(x) for x in (self.timeout, self.interval, self.cache_seconds))
            or self.timeout <= 0
            or self.interval < 0
            or self.cache_seconds < 0
        ):
            raise ValueError("positive timeout and nonnegative interval/cache required")
        parsed = urlparse(url)
        if parsed.scheme not in ("https", "http") or not parsed.netloc:
            raise ValueError("public data requires an HTTP(S) URL")
        cached = self._cache.get(url)
        if cached and time.monotonic() - cached[0] < self.cache_seconds:
            return cached[1]
        for attempt in range(3):
            time.sleep(max(0, self.interval - (time.monotonic() - self._last_request)))
            self._last_request = time.monotonic()
            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FinanceToolkit research)",
                    "Accept": "text/html,application/json,application/xml",
                },
            )
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    text = response.read().decode("utf-8")
                self._cache[url] = (time.monotonic(), text)
                return text
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise ProviderError(f"HTTP {exc.code} from {url}") from exc
                time.sleep(min(10, 2 ** (attempt + 1)))
            except (URLError, TimeoutError, UnicodeError) as exc:
                raise ProviderError(f"Unable to retrieve {url}: {exc}") from exc
        raise ProviderError(f"Unable to retrieve {url}")

    def json(self, url: str):
        try:
            return json.loads(self.text(url))
        except ValueError as exc:
            raise ProviderError(f"Expected JSON from {url}") from exc
