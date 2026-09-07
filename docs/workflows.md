# Research workflows

Examples use synthetic inputs unless `--live` is supplied. Public data needs `.[data]`;
model, chart and sentiment examples need their respective extras. No account is needed
for the public workflows below.

## Discover and research companies

```bash
python examples/research_watchlist.py --live --output ./research
python examples/research_company.py --live
```

The watchlist example downloads the first 20 large-company matches with quarterly EPS
growth above 10%, enriches them, and explains the growth, margin, ownership and P/E checks.
The HTML and CSV reports include all examined candidates, including failures of the screen.
This is a bounded sample, not a complete market scan.

```python
from finance.data import Finviz, fetch_many
from finance.screening import growth_screen

provider = Finviz()
universe = provider.screen(['cap_largeover', 'fa_epsqoq_o10'], limit=100)
batch = fetch_many(universe.index, provider.company)
print(batch.errors)  # Failed tickers remain visible.
result = growth_screen(batch.table())
```

Finviz filters use the codes in its public screener URLs. `screen` reports `total_matches`
and `complete` in DataFrame attributes. `universe('dow')` and `universe('russell2000')`
use Finviz's current index classifications; they are not licensed historical constituent
records. `snapshot_changes(before, after)` compares snapshots you have actually collected.
It cannot reconstruct earlier membership or recommendations.

`YahooFinance.statements(ticker, kind, frequency)` accepts `income`, `balance`, `cashflow`
and `annual`/`quarterly`. Rows are reporting periods; fields retain provider statement names.
`statement_ratios` calculates margins, average-equity ROE, leverage and current ratios.
`company_cash_flows` estimates operating-company FCFF from after-tax operating income,
depreciation, signed capex and working-capital cash changes. Missing latest-period inputs
raise an error. Review source currency, fiscal dates and assumptions before valuation.

`company_scenarios` accepts explicit annual growth paths, discount rate, cash, debt and
shares. `index_scenarios` values index dividends from EPS, payout and recovery paths; the
example's index inputs are illustrative, not scraped estimates.

## Signals and strategy evaluation

```bash
python examples/research_strategies.py --live
```

This compares moving-average, MACD, Keltner, stochastic, Williams %R and Ichimoku signals
with several stop thresholds on a training period. Only the selected configuration runs
on the later holdout. Each signal family is also callable independently.

```python
from finance.backtesting import backtest, completed_trades, trade_statistics
from finance.strategies import macd_trend

result = backtest(
    prices.open, prices.close, macd_trend(prices.close, short=True),
    high_prices=prices.high, low_prices=prices.low,
    stop_loss=.08, take_profit=.20, trailing_fraction=.10,
    commission=.001, liquidate=True,
)
print(trade_statistics(completed_trades(result.trades)))
```

Protective orders use observed high/low ranges. Gaps execute at the open; ambiguous
same-bar stop/profit hits use the stop first. Trailing levels update after the bar.
A stopped position waits for the source target to change before rearming. These assumptions
cannot recover an intrabar price path from daily bars.

`completed_trades` matches FIFO lot portions and apportions commissions. Its statistics
count matched lots; borrow costs remain an account-level expense. Partial closes can produce
multiple rows for one position. Open lots are not treated as completed trades.

`green_line_screen` builds a proximity watchlist using completed months. `rsi_trend_screen`
combines price above its SMA with a two-observation RSI average. `seasonal_entries` reports
actual entry/exit dates and forward returns; `seasonal_summary` compares a supplied universe.
Selecting seasonal dates after looking at their results is in-sample research.

## Models and distributions

```bash
python examples/research_models.py --live
python -m pip install -e '.[neural,prophet]'
python examples/research_models.py --live --neural --prophet
```

`forecast_latest` fits known labels and predicts from the latest close. Evaluate the chosen
model with `evaluate_forecast` before interpreting that output. `select_arima_order` uses
training BIC; `arima_forecast` returns future observation steps and model-based intervals.
Future step numbers deliberately make no assumption about exchange holidays.

`arima_diagnostics` provides stationarity/residual checks and retrospective decomposition.
`factor_analysis` reports loadings, communalities, KMO and Bartlett diagnostics.
`volatility_regimes` fits a mixture on earlier rolling volatility and returns later state
probabilities. `student_t_fit` estimates degrees of freedom, location, scale and quantiles.
`partial_correlations_cv` selects regularization for a descriptive dependence network.

LSTM/CNN experiments predict next-observation returns using earlier windows. Prophet uses
a fixed-origin log-price forecast. All report held-out errors against simple baselines.
Changing architectures or parameters repeatedly after inspecting those errors turns the
holdout into tuning data; reserve another period for a final assessment.

## News, calendars and external signals

```bash
python examples/research_news.py --live
```

`Finviz.news()` discovers market-wide headlines; pass a ticker for company headlines.
`Finviz.insiders()` retrieves recent market-wide insider activity, and `analysts(ticker)`
returns dated rating/target changes. `market()` exposes movers, today's macro calendar,
futures and FX/bond summaries. `earnings_calendar(start, end)` uses Nasdaq for up to 31 days.

`rss_news(url)` reads public RSS feeds. `transcript_index()` discovers recent Motley Fool
transcripts; `article_text(url)` retrieves accessible article text. `sentence_sentiment`
keeps the sentence evidence behind language scores. Do not interpret those scores as
measures of investment quality or expected returns.

`TradingView().recommendations(['NASDAQ:AAPL'], interval='1d')` retrieves public scanner
recommendations. This is an undocumented snapshot endpoint, not a licensed historical feed.
Use `YahooFinance.history(..., interval='5m')` for intraday bars within provider retention.

`reddit_posts` attempts public recent-post retrieval and fails explicitly if access is
blocked. Reddit rejected anonymous requests during verification. `social_mentions` can
analyze supplied post tables (`id`, `text`) against an explicit ticker universe. Anonymous
X search/timeline collection is not provided; access has not been established reliably.

## Charts, reports and the app

```bash
python -m pip install -e '.[apps,reports,sentiment]'
streamlit run apps/research.py
```

The app covers stock charts, indicator overlays, strategy results, company discovery,
valuation, headlines and portfolio allocation. Indicators and calculations use the same
Python functions as the examples. Data is fetched when an analysis is submitted.

`candles`, `equity_chart` and `correlation_heatmap` return matplotlib figures.
`export_table` writes CSV or Excel; `research_report` writes standalone HTML tables.
`network_gexf` exports signed dependence edges for Gephi. `gann_fan` requires explicit
price-per-bar units, and `speed_resistance` exposes lines only once a supplied swing has
completed. These are drawing conventions, not evidence of predictive value.

## Optional delivery and brokerage

```bash
python examples/preview_order.py
```

This only constructs an order, illustrates partial-fill reconciliation and previews an
email. Nothing is submitted or sent. `email_report` creates a message; `send_email`,
`send_sms` and `send_webhook` perform explicit deliveries using your credentials/destination.
For scheduled reports, invoke the watchlist example from your existing OS scheduler and
send its output through the chosen transport. The library does not install background jobs.

`Alpaca` exposes account, positions, recent orders, client-ID lookup, limit-order submission
and cancellation. It defaults to Alpaca's paper endpoint. Supply credentials explicitly;
never put them in source files. Live submission additionally requires `allow_live=True`.
`reconcile_orders` distinguishes partial fills and unknown orders. After a submission timeout,
look up the original client ID before deciding whether to retry; unknown does not mean rejected.

Brokerage and delivery transports have offline contract checks. Account-connected execution
and actual delivery have not been verified because no credentials were supplied. There is
no Robinhood equity client or unattended live-trading bot. Alpaca account access is required
for connected stock execution; scraping cannot replace brokerage authentication.
