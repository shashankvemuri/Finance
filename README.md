# Finance

Finance is a Python toolkit for market data, technical indicators, financial analysis,
stock screening, strategy research, backtesting, portfolios and statistical models.
Version 2 consolidates the original collection into reusable calculations with explicit
inputs, small dependencies and tested execution conventions. Models and trading rules are
research tools; runnable examples are the starting point.

## Install

Python 3.12 or newer:

```bash
git clone --branch finance-v2 https://github.com/shashankvemuri/Finance.git
cd Finance
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

Core dependencies are NumPy and pandas. Add only the features you need:

```bash
python -m pip install -e '.[data]'             # Yahoo Finance and constituent tables
python -m pip install -e '.[portfolio,models]' # Optimization and statistical/ML experiments
python -m pip install -e '.[plot,sentiment]'   # Charts and VADER text scoring
```

## Use

Download normalized, consistently adjusted OHLCV with the `data` extra:

```python
from finance.data import YahooFinance

prices = YahooFinance().history('AAPL', '2023-01-01', '2025-01-01')
```

Calculate indicators without any network access:

```python
from finance.indicators import bollinger_bands, rsi

strength = rsi(prices['close'], window=14)
bands = bollinger_bands(prices['close'], window=20)
```

Generate close-time signals and execute them at the next open:

```python
from finance.backtesting import backtest
from finance.strategies import moving_average

targets = moving_average(prices['close'], fast=20, slow=50)
result = backtest(prices['open'], prices['close'], targets, commission=0.001)
print(result.metrics)
```

Returns and rates are fractions; RSI is 0–100. Warm-up values remain missing. The modest
backtester tracks cash, fractional shares, long/short fills, commission, slippage and borrow
costs. Read the [calculation and execution conventions](docs/methodology.md) before interpreting results.

## Explore

| Area | Capabilities |
| --- | --- |
| `data` | OHLCV/intraday, dividends, earnings, company snapshots, news, insiders, universes, CFTC positioning |
| `indicators` | Moving averages, momentum, volatility/channels, volume, rolling statistics, pivots and breadth |
| `analytics` | Returns, performance, CAPM/OLS, VaR, Kelly, valuation, seasonality and optional text sentiment |
| `screening` | Relative strength, Minervini diagnostics, RSI, growth/value and dividend screens |
| `strategies` | Crossovers, trend, mean reversion, breakouts, close-based stops and pairs experiments |
| `backtesting` | Shared next-open execution, fill journal, equity/cash accounting and benchmark metrics |
| `portfolio` | Allocation, constrained optimization/frontier, correlated simulation and lump sum versus DCA |
| `models` | Chronological baseline evaluations, ARIMA, PCA, clustering, cointegration and anomalies |

[Examples](examples) use seeded synthetic bars by default. Add `--live` for Yahoo data;
`download_market_data.py` always uses the network.

```bash
python examples/calculate_indicators.py
python examples/backtest_moving_average.py --live
python examples/optimize_portfolio.py
python examples/forecast_time_series.py
```

Current constituents and fundamentals are snapshots, not historical point-in-time inputs.
Public providers can throttle or change schemas; see [provider contracts](docs/providers.md).
Forecast experiments report held-out errors against simple baselines and make no claim of
predictive advantage. No brokerage execution or notification service is included.

## Contribute

```bash
python -m pip install -e '.[data,portfolio,models,sentiment,plot,dev]'
ruff check .
ruff format --check .
python -m pytest
python audit/run_examples.py
```

CI runs core and optional-feature tests on Python 3.12–3.14 without live network requests.
[Verification evidence](audit/README.md) includes independent numerical comparisons and real
executions. [MIGRATION.md](MIGRATION.md) accounts for every original Python file; old sources
remain in Git history. Keep calculations separate from providers and add regression tests
for numerical or execution changes.

Created by [Shashank Vemuri](https://github.com/shashankvemuri). [MIT License](LICENSE).
The original technical-indicator collection drew on
[Stock_Analysis_For_Quant](https://github.com/LastAncientOne/Stock_Analysis_For_Quant/tree/master/Python_Stock/Technical_Indicators)
by LastAncientOne.

## Disclaimer

*The material in this repository is for educational purposes only and should not be considered professional investment advice.*
