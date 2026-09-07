# Finance v2 progress

## Completed
- Clean starting checkout; created `finance-v2` from `12dac57c7f62146f7073ccc17f64bc45fd687b5d`.
- Enumerated all 183 Python files and tracked assets; initialized per-file migration ledger before deletions.

## Current work
- Read legacy calculations and run programs in isolated subprocesses.
- Establish Python 3.12+ environment and numerical references.

## Verification
- `git status --short`, `git ls-files`, source and dependency inventory.

## Known issues
- Duplicate ATR definitions; WMA mislabeled; Astral Timing negative indexing.
- Bundled browser binary and stale ticker snapshots; no tests or package configuration.

## Remaining
- Audit/run all meaningful files; implement all eight package domains and examples.
- Independent numerical checks, real data workflows, models evaluation, CI, Ruff, tests.
- Disposition review, remove superseded code, rewrite README last.

## Implementation checkpoint
- Isolated audit attempted every non-side-effect legacy program: 98 removed pdr_override failures, 12 missing Adj Close failures, other dependency/API/input failures recorded per file in audit/legacy_runs.json. Notification/order/browser/server programs source-reviewed without executing side effects.
- Implemented modern packaging (Python >=3.12, NumPy/Pandas core), data normalization/provider boundary, broad indicator families, returns/risk/valuation/regression analytics, concrete screens, shared strategies/backtesting, portfolio optimization/simulation and optional modeling.
- First live execution: AAPL 2023-01-01 through 2025-01-01, 502 rows. RSI range 22.22..90.12; 20/50 SMA backtest 9 fills, total return .4724, max drawdown -.1309. Preliminary only; independent tests still pending.
- Commands: `.venv/bin/python audit/run_legacy.py`; `.venv/bin/pip install -e '.[data,portfolio,models,sentiment,dev]'`; initial live API execution; initial Ruff check.
- Remaining: complete detailed concept dispositions, deeper legacy probes, numerical reference suite and adversarial accounting tests, all runnable examples, live provider verification and model baselines, CI and final docs. No legacy source deleted yet.

## Verification checkpoint
- 119 deterministic tests pass; Ruff passes for package/tests/examples. Published Wilder RSI, independent `ta` formulas including ADX/ATR, analytical min-variance/max-Sharpe, direct fill accounting, GBM moments and model-prefix checks are covered.
- All 14 offline examples executed successfully. Live example sweep and comprehensive live verification running.
- Second legacy diagnostic pass: 71/82 indicator scripts complete with explicit downloader shims and real cached AAPL/QQQ/SPY/GSPC/META/CRON/RIG/AMD/NIO bars. Remaining errors include removed ix/iteritems, bad WMA keyword, undefined variables, broken plot options and unavailable Quandl dependency. Direct execution failures remain separately recorded.
- All 183 legacy Python paths have explicit reviewed concept dispositions in audit/dispositions.json and rendered MIGRATION.md. Scope removals and formula corrections are documented; no legacy sources removed yet.
- Found/fixed provider edge: valid Nasdaq ticker NA was parsed as missing; directory now returns 13,155 listings. Nasdaq calendar has mixed numeric/string amounts and indicated_Annual_Dividend field; parser corrected.
- Added Python 3.12/3.13/3.14 core/full CI matrix and methodology/provider documentation. README remains unchanged pending final implementation review.

## Live verification completed
- `python audit/verify_live.py` passed on six real assets over 2022-2024; 58 indicator APIs and ten provider workflows including 105 CFTC reports, 70 calendar rows, 503 S&P500 constituents, 13,155 exchange listings and 312 intraday bars.
- AAPL 20/50 SMA: 17 fills, 14.495% return, -28.613% maximum drawdown, independently reconciled final equity $11,449.51 (commission .001, slippage .0005).
- Minervini diagnostics returned JPM as passing within the five-stock test universe; every individual criterion retained for inspection.
- Portfolio weights/constraints and reported statistics independently checked. Simulation mean $15,739.75 versus analytical $15,652.80 (10,000 paths); no impossible paths.
- Five return forecasters, ARIMA, GaussianNB, PCA, K-means/mixture, feature clustering, graphical lasso, cointegration and anomalies executed. Most predictors did not outperform their baseline; all retained as research experiments, no alpha claims.
- All 15 examples executed with live mode; all 14 network-optional examples also executed offline. Output evidence saved in audit/examples_*.json.
- `ruff check .` passes. Build and clean core-only installation checks underway; hosted CI has not yet been run.

## Legacy retirement
- Core-only clean installation passed: 99 tests, 13 explicit optional-dependency skips. Wheel and sdist built successfully.
- Committed the v2 package, tests, examples, CI, methodology, provider docs and all per-file dispositions before legacy deletion (`93a6a61`).
- Final direct audit rerun materialized original source and ticker CSVs per program, eliminating working-directory artifacts. Initial run retained separately. Legacy audit scripts now recover baseline source from Git after retirement.
- Removed 183 superseded Python paths, obsolete requirements.txt, five stale ticker CSVs and checked-in chromedriver, only after checking every path against MIGRATION.md.
- Remaining: final source review, accurate README, post-retirement checks, dedicated-branch push and hosted CI verification.
