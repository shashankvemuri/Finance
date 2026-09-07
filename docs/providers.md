# Data providers

Install `.[data]` for Yahoo Finance, Finviz and HTML parsing. Pure calculations need no data
extra. `YahooFinance.history(ticker, start, end, interval='1d')` returns one normalized OHLCV
frame with a date index, lowercase columns, positive prices and nonnegative volume. End is
exclusive. Intraday history has provider retention limits. `adjusted=True` is explicit;
set it false for unadjusted OHLC. Timestamps preserve exchange timezone when available.

`company`, `earnings`, `dividends`, `news` and `insider_transactions` are current-provider
adapters. Company ratios use fractional units; `analyst_rating` is the vendor's numeric
recommendation summary. Earnings may legitimately have missing estimates or actual EPS.
A missing disclosure table raises `ProviderError` rather than silently returning fabricated
empty data. A security with a valid price history and no dividends returns an empty dividend
Series. Known empty Nasdaq calendar days return an empty table with the documented schema.

`sp500_constituents()` returns current ticker/name/sector. `exchange_universe()` reads Nasdaq
Trader's two listing files, excludes test issues and retains the ETF flag and native symbol.
It preserves `NA` as a ticker. Exchange codes and special preferred/warrant share symbols
are exchange-native; translate them for the chosen provider, rather than treating every
listing as a Yahoo common-stock symbol. `normalize_ticker` handles ordinary Yahoo share-class,
index and FX symbols, not every exchange suffix convention.

`dividend_calendar(date)` returns Nasdaq ex-dividend/payment/record dates and reported
amounts. `cot_financial_futures(contract_code, start, end)` uses CFTC TFF futures-only
positioning; for example, `13874A` identifies the E-mini S&P 500 contract.
The date interval is start-inclusive/end-exclusive and limited responses fail explicitly.

Network operations have timeouts and schemas are checked. These are public/unofficial
interfaces, not exchange-grade service contracts: throttling, revisions, schema changes and
unavailable fields remain possible. Yahoo and Nasdaq website APIs may change independently
of their client libraries. S&P500 membership still uses a maintained HTML table because
there is no bundled licensed index feed. There is no automatic cross-provider fallback that
could silently mix adjustment bases or currencies. Honor provider terms and data licensing.

Ordinary tests mock transport and never require network access. After installing
`.[data,portfolio,models,dev]`, run `python -m pytest --live -m integration` to check provider
schemas and financial workflows against real data. Daily checks use a fixed historical
period; intraday checks use the last two weeks. Use `python scripts/check_examples.py --live`
to run examples with public data (install the extras listed in the README). Live checks are
opt-in and excluded from CI; provider failures are reported as test failures.


Finviz provides public screener, company, analyst, insider and news snapshots. Fetching uses
bounded retries for throttling/transient server errors, per-client request spacing and a
short in-memory cache. Pagination rejects duplicate rows and changing result counts;
explicit limits are reported through `complete` and `total_matches` attributes. An HTTP 200
response without the expected table is an error, not an empty result. Percentages normalize
to fractions; multiple measures inside a cell remain distinct. Native ticker symbols are
preserved. Homepage macro/futures/FX values retain their source strings and units.

Yahoo statement rows identify reporting-period ends, not filing availability; historical
statements may be restated. Statement currency and retrieval time are recorded. Analyst
rating/target changes retain vendor text because scales differ between research firms.
News `source_time` retains the displayed time; it must not be treated as a normalized UTC
publication timestamp. RSS feeds provide parsed UTC dates when supplied by the publisher.

TradingView's public scanner was verified for current recommendations, but it is undocumented
and may change or become inaccessible. Intraday OHLCV comes from Yahoo, with Yahoo's retention
limits. Public Motley Fool transcripts were verified by article URL. Reddit anonymous access
returned HTTP 403; its adapter reports that failure. Anonymous X collection and authenticated
brokerage/delivery have not been verified. See [workflows](workflows.md) for supported entry points.
