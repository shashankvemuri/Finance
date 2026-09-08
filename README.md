# Finance

Finance is a Python toolkit for market data, technical indicators, financial analysis,
stock screening, strategy research, backtesting, portfolios and statistical models.
Calculations use explicit inputs, a small dependency set and tested execution conventions.
Models and trading rules are research tools; runnable examples are the starting point.

## Install

Python 3.12 or newer:

```bash
git clone https://github.com/shashankvemuri/Finance.git
cd Finance
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

Core dependencies are NumPy and pandas. Add only the features you need:

```bash
python -m pip install -e '.[data]'             # Public data, Finviz and financial statements
python -m pip install -e '.[portfolio,models]' # Optimization and statistical/ML experiments
python -m pip install -e '.[plot,sentiment]'   # Charts and VADER text scoring
python -m pip install -e '.[apps,reports]'     # Interactive app and Excel exports
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
| `data` | OHLCV/intraday, Finviz discovery, statements, calendars, analysts, news, transcripts, insiders and universes |
| `indicators` | Moving averages, momentum, volatility/channels, volume, rolling statistics, pivots and breadth |
| `analytics` | Returns, CAPM/OLS, risk, statement ratios, company/index valuation, seasonal studies and sentiment |
| `screening` | Relative strength, Minervini, Green Line, RSI/trend, growth/ownership and dividend screens |
| `strategies` | Crossovers, MACD, Keltner, Ichimoku, oscillator reversion, pairs and chronological strategy selection |
| `backtesting` | Next-open execution, long/short protective orders, FIFO trade reports, cash accounting and benchmarks |
| `portfolio` | Allocation, constrained optimization/frontier, correlated simulation and lump sum versus DCA |
| `models` | Forecasts/baselines, ARIMA diagnostics, PCA/factors, regimes, clustering, networks and optional neural/Prophet experiments |
| `reports` | Candlesticks, heatmaps, equity charts, CSV/Excel, HTML reports and graph exports |
| `integrations` | Explicit notification transports, order previews and an optional Alpaca client |

[Examples](examples) use synthetic inputs by default. Add `--live` for public data;
`download_market_data.py` always uses the network.

```bash
python examples/calculate_indicators.py
python examples/backtest_moving_average.py --live
python examples/optimize_portfolio.py
python examples/research_watchlist.py --live
python examples/research_models.py
streamlit run apps/research.py
```

Current constituents and fundamentals are snapshots, not historical point-in-time inputs.
Public providers can throttle or change schemas; see [provider contracts](docs/providers.md).
Forecast experiments report held-out errors against simple baselines and make no claim of
predictive advantage. Heavy models and apps are optional; brokerage and delivery require
separate credentials. See [research workflows](docs/workflows.md) for full examples,
optional installs and provider limitations.

[Contributing](CONTRIBUTING.md)

Created by [Shashank Vemuri](https://github.com/shashankvemuri). [MIT License](LICENSE).
Technical-indicator references include
[Stock_Analysis_For_Quant](https://github.com/LastAncientOne/Stock_Analysis_For_Quant/tree/master/Python_Stock/Technical_Indicators)
by LastAncientOne.

## Disclaimer

*The material in this repository is for educational purposes only and should not be considered professional investment advice.*
