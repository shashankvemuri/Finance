# Finance v2 progress

Status: implementation complete on `finance-v2`. All eight migration areas are implemented,
the original code is accounted for, and the hosted core/full CI matrix passes.

## Completed migration areas

- **Audit:** inventoried all 183 original Python files before deletion. Directly executed every
  eligible program with realistic symbols, bounded runtime and isolated original files; recorded
  ten exclusions for external message/order/browser/server side effects. Inspected successful
  output rather than equating exit zero with success. Final direct runs found 100 removed
  `pdr_override` failures and 13 missing `Adj Close` failures, among other recorded causes.
- **Deeper diagnostics:** 71/82 original indicators executed with explicit downloader shims and
  real cached 2023–2024 bars. Direct and shimmed evidence remain separate.
- **Data:** normalized OHLCV and intraday, company snapshots, dividends/calendar, earnings, news,
  insider records, maintained current universes, CFTC TFF positioning. Timeouts/schema checks.
- **Indicators:** canonical averages, trend, momentum, volatility, volume, relative/statistical,
  level and breadth calculations. Corrected numerical definitions and causal availability.
- **Analytics/screens:** return/risk/performance, CAPM/OLS, valuation/scenarios, seasonality,
  optional sentiment; relative strength/IBD-inspired, Minervini, RSI, quality/growth/dividend screens.
- **Strategies/backtesting:** shared pure targets, trend/reversion/breakout/pairs rules and
  close-based stops; next-open fills, long/short cash accounting, costs, borrow, benchmark metrics.
- **Portfolio:** labeled return/risk, constrained optimization/frontier, discrete/random allocation,
  correlated GBM, Monte Carlo risk, comparable-budget DCA/lump sum.
- **Models:** chronological/purged return forecasting, ARIMA/persistence and probabilistic
  baselines, PCA, K-means/mixtures, graphical lasso, cointegration and novelty experiments.
- **Delivery:** NumPy/pandas core, optional extras, Python >=3.12, 15 runnable examples, package
  builds, Ruff, pytest, six-job CI, concise README, provider/methodology docs and original license.
- **Retirement:** removed only after per-file decisions and replacement verification were committed:
  183 superseded Python paths, 46-package requirements.txt, five stale universe CSVs, chromedriver.
  Baseline `12dac57` remains in Git history and audit scripts recover it automatically.

## Verification performed

- `python -m pytest -q`: **121 passed** with full extras.
- Clean core-only installation: **100 passed**, optional suites explicitly skipped. Hosted jobs
  confirm core and full installs independently on Python **3.12, 3.13 and 3.14**.
- `ruff check .`, `ruff format --check .`, `python -m build`, `git diff --check`: pass.
- `python audit/run_examples.py`: all 14 offline-capable examples pass.
- `python audit/run_examples.py --live`: all 15 entry points pass.
- `python audit/verify_live.py`: six real assets, 58 indicator APIs, ten provider workflows,
  screening, backtests, portfolio constraints, simulation, valuation, model baselines/structure.
- Independent checks: published Wilder RSI; `ta` comparisons including ADX/ATR/CCI/stochastic;
  hand-computed volume and P&L fixtures; inverse-variance/tangency solutions; OLS/perpetuity
  identities; prefix causality; cash reconstruction; analytical GBM expectation and variance.
- Real AAPL 2022–2024 SMA test: 17 fills, 14.495% return, -28.613% max drawdown,
  independently reconciled final equity **$11,449.51** with .001 commission/.0005 slippage.
- Real simulation mean **$15,739.75**, analytical mean **$15,652.80** over 10,000 paths.
- Live providers returned 503 S&P500 constituents, 13,155 exchange listings, 70 calendar rows,
  312 intraday bars and 105 CFTC positioning reports, plus valid company/news/disclosure records.
- Final optimizer recheck: two constrained allocations and 20 real-data frontier points;
  results in `audit/optimizer_verification.json`.
- Hosted run [34138879212](https://github.com/shashankvemuri/Finance/actions/runs/34138879212)
  passed all six jobs. Exact validated code revision and jobs are in `audit/ci_verification.json`.

## Correctness issues resolved during verification

- Valid Nasdaq ticker `NA` parsed as missing; preserve exchange-native symbols.
- Nasdaq dividend amounts vary between numeric and string values; normalize both.
- Initial hosted Linux run exposed SLSQP iteration failure at a constrained frontier point.
  Added analytical objective/equality derivatives and redundant-constraint handling; endpoint
  and equal-return tests added. Subsequent full matrix passes without loosening constraints.
- Historical raw-return compounding, future-index reads, same-close fills, cash/position confusion,
  wrong WMA/CCI/MFI/PVT/ADX formulas and DCF timing are corrected and described per file.

## Current work and remaining scope

No required implementation work remains. Final verification records and branch state are being
finalized; source code is validated by hosted CI. README and ledger describe the actual v2 API.

Public Yahoo/Nasdaq interfaces, S&P500 HTML and CFTC endpoints remain provider-dependent. Current
fundamentals/universes are not point-in-time data; intraday retention and schemas can change.
Most evaluated ML models did not beat their baseline. They are explicitly experiments.

Intentionally future work: historical licensed universes/statements/transcripts, market-wide
fundamental/earnings aggregation, richer execution/liquidity/margin modeling and evidence-backed
sequence architectures. Brokerage/SMS/email/social-crawler integrations and scale-dependent Gann
predictions are outside v2 scope. These are explicit dispositions, not unfinished supported APIs.
