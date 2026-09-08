# Calculation and execution conventions

Returns, volatility, yields and rates are fractions (`.10` means 10%). ROC and RSI use
percent/0–100 scales as stated in their APIs. Price series must be positive, indexed in
increasing order and unique. Calculations retain indexes and warm-up NaNs; missing market
observations are never forward-filled. Multi-input calculations require explicit alignment.
Use the same adjustment basis for all OHLC fields. Yahoo's adjusted OHLC approximates total
returns through historical adjustment factors; it is not a literal cash-dividend ledger.

## Indicators

EMA is recursive (`adjust=False`), seeded at the first observation with N-1 hidden warm-up
rows. Wilder smoothing seeds a full-window arithmetic mean and then uses alpha=1/N. RSI
requires N changes, uses Wilder gain/loss smoothing, and returns 50 for a flat window.
ATR starts with high-low for the first range. ADX requires a previous bar for directional
movement and first becomes available at zero-based bar 2N-1. These initialization conventions
can differ from vendor charts with longer hidden histories.

Bollinger Bands use population standard deviation; rolling variance/volatility use sample
standard deviation. WMA uses weights 1..N. TRIMA's total triangular kernel spans N bars.
VWMA is a rolling weighted mean; VWAP is cumulative, optionally reset using caller-supplied
exchange-session labels. TWAP assumes equal intervals. Zero volume yields undefined VWAP,
not an invented price. Typical price is `(high + low + close) / 3`; choose it explicitly
when passing the price argument to VWAP.

Pivot inputs are bars at the desired pivot frequency; outputs use the previous completed
bar. Local extrema are emitted on their confirmation date, not retrospectively at the
extreme. Green Line accepts completed monthly highs and confirms an all-time high after
three subsequent lower months. Exclude the current incomplete month before calling it.
Breadth counts describe the supplied universe. McClellan uses ratio-adjusted advances minus
declines and the 19/39 EMA difference.

Dynamic momentum, lag reversal and log-ratio pairs signals are experiments. They are
causal rule implementations, not evidence of profitability. Ichimoku spans are returned
without chart projection. No projected or centered plot values are used as future data.

## Backtesting

Signals are target exposures known at close t. The engine executes at open t+1. The last
signal cannot execute without another bar. It trades on target changes, or every bar with
`rebalance=True`. It holds fractional shares between changes; weights may drift with prices.
Gross target exposure is capped at one. Prices must share asset columns, timestamps and
adjustment basis. Cash, shares, fees and mark-to-market equity are reconciled separately.

The engine solves for post-transaction equity before sizing orders, including commission
and directional slippage. Short proceeds are credited to cash and the liability is marked
at each close. Annual borrow charges accrue per held bar using opening short notional.
Cash earns zero interest; the engine raises on insolvency. This is a research engine without
margin loans, tick-level order sequencing, dividends as separate cash flows, market impact,
liquidity constraints or a borrow-availability model. Short simulations therefore need
additional execution assumptions before any real-world interpretation.

The optional final close liquidation is precommitted, independent of that day's signal.
Trade rows are fills, including reversals and partial rebalances, not inferred round trips.
The benchmark is a cost-free equal-dollar buy-and-hold basket bought at the first open.
Close-based signal stops execute at the next open, which may gap past the threshold.
Optional engine protective orders require high/low inputs. Gap fills use the opening price;
when both thresholds occur within a bar, stops take priority unless the open already crosses
the profit threshold. Trailing levels use extrema from completed bars. Stops are anchored at
the initial fill of a position, including through partial rebalances. Rearming requires a
source-target change. Borrow is charged for the opening short exposure even if stopped that bar.
FIFO completed-lot reports allocate commissions by quantity; borrow stays at account level.

Performance uses compounded simple returns and includes initial capital in the drawdown
peak. Volatility is annualized sample deviation; Sharpe subtracts an annual risk-free rate
converted to one bar. Undefined zero-volatility ratios remain NaN. VaR/expected shortfall
are nonnegative loss fractions for one supplied observation period; no automatic horizon
scaling or normality assumption is applied to historical VaR.

## Portfolios and valuation

Optimization takes labeled means and covariance in the same time unit as the risk-free
rate, usually annual. Bounds, sum-to-one, solver success and target return are verified.
The maximum-Sharpe solver requires positive expected excess return in at least one asset.
Historical estimates are inputs, not forecasts. Frontier output covers the efficient branch
above the global minimum variance return. Constant-weight portfolio returns imply periodic
rebalancing before costs; the backtester models actual share holdings and costs.

GBM uses annual arithmetic drift, a minus-half-variance log correction, correlated shocks,
explicit horizon and a local random seed. Portfolio simulation is fixed-share buy-and-hold,
not a continuously rebalanced portfolio. DCA and lump sum share the same initial budget;
uninvested DCA cash remains in account value and earns zero interest.

DCF cash flows arrive at year end starting at year one. Terminal value sits at the final
forecast year; discount rate must exceed terminal growth. Unlevered enterprise cash flows
are discounted at WACC, then cash is added and debt subtracted. Per-share dividends can use
the same formula with equity discount rate and zero debt/cash adjustments. Do not treat
Yahoo's reported free cash flow as automatically unlevered cash flow. Scenario examples
state assumptions; their values are not investment recommendations. The statement workflow
estimates operating-company FCFF as after-tax operating income plus depreciation, signed capex
and working-capital cash changes. Stock compensation is not added back. This approximation
is inappropriate for banks. Annual scenario growth requires annual base cash flow.

## Models and provider dates

Forecast features are observable at close t and predict the return to t+h. A chronological
holdout purges h feature rows at the training boundary so no training label reaches into
test time. Scaling is fitted only on training rows; estimator tuning is not performed on
the holdout. Compare errors with a zero-return baseline. ARIMA uses one fixed forecast origin
and the matching persistence baseline. Gaussian direction probabilities use held-out Brier
and log loss against a training-prior baseline. No model is advertised as predictive alpha.

PCA, clustering and graphical lasso are descriptive analyses of the supplied sample. Asset
clustering orients assets as samples; indicator clustering accepts one feature row per asset.
Isolation Forest fits only earlier observations. Cointegration tests belong on a formation
sample; Holm adjustment accounts for the tested pair family, not all researcher's choices.

S&P500 and exchange lists are **current** snapshots. Historical backtests using them have
survivorship bias. Fundamentals/analyst/news snapshots must not be backdated into historical
signals. CFTC report dates are position dates, not publication dates; obtain actual release
timestamps before turning positioning into a historical trading rule. Insider transaction
dates similarly do not establish when a filing became available.

## Independent references

- [Wilder RSI formula and initialization](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi)
- [Technical Analysis Library for Python source](https://github.com/bukosabino/ta): independent comparisons for moving averages, ATR, ADX, CCI, stochastic, TSI, Ultimate Oscillator, bands and volume metrics. Initialization differences are explicit in tests.
- [scikit-learn time-series splitting](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) and [leakage prevention](https://scikit-learn.org/stable/common_pitfalls.html)
- [Nasdaq Trader directory schema](https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs)
- [CFTC report datasets and publication distinction](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm)

Tests also use hand-computed fixtures, the two-asset inverse-variance/tangency solutions,
OLS equations, a perpetuity identity, independently reconstructed fills and analytical GBM
moments. Prefix-invariance tests check that future data does not change prior indicators,
signals or equity, including protective orders. Provider contract tests use mocked responses; `pytest --live -m integration`
checks real data and financial workflows.
