# Contributing

Keep calculations separate from providers and presentation. Prefer small functions with
explicit inputs and outputs. Public APIs should state non-obvious columns, index meaning,
units, missing-data behavior and financial assumptions in short docstrings.

## Find your starting point

Public imports live in each area's `__init__.py`. Paths below are relative to the repository
root; test filenames are under `tests/` and example filenames under `examples/`.

| Change | Source | Example | Focused tests |
| --- | --- | --- | --- |
| Provider or index universe | `src/finance/data/` | `research_watchlist.py`, `download_market_data.py` | `test_public_sources.py`, `test_provider_contracts.py` |
| Indicator | `src/finance/indicators/` | `calculate_indicators.py` | `test_indicators.py` |
| Returns, risk or valuation | `src/finance/analytics/` | `analyze_stock_returns.py`, `value_a_company.py` | `test_analytics.py`, `test_research_math.py` |
| Stock screen | `src/finance/screening/` | `screen_minervini.py` | `test_data_screening.py`, `test_research_math.py` |
| Signal or execution rule | `src/finance/strategies/`, `src/finance/backtesting/` | `backtest_moving_average.py`, `select_strategy.py` | `test_backtesting.py`, `test_research_math.py` |
| Allocation or simulation | `src/finance/portfolio/` | `optimize_portfolio.py`, `simulate_portfolio.py` | `test_portfolio.py` |
| Forecast or clustering | `src/finance/models/` | `forecast_time_series.py`, `research_models.py` | `test_models.py`, `test_research_models_reports.py` |
| Report or dashboard | `src/finance/reports/`, `apps/research.py` | `research_watchlist.py` | `test_research_models_reports.py`, `test_app.py` |
| External integration | `src/finance/integrations/` | `preview_order.py` | `test_research_models_reports.py` |

For example, an indicator change starts with its public import, the calculation and the
existing fixtures. Run `python -m pytest tests/test_indicators.py` and
`python examples/calculate_indicators.py`; inspect alignment, warm-up values and ranges.
For a strategy change, inspect fill timestamps and reconcile cash plus holdings with equity.
For a provider change, use saved or synthetic responses in offline tests and inspect
completeness, missing fields and source timestamps in an explicit live run.

## Verification

Run commands from the repository root with Python 3.12 or newer. Start with a fresh virtual
environment so installed optional packages do not disguise a missing dependency:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[data,portfolio,models,sentiment,plot,reports,dev]'
export MPLBACKEND=Agg
python -m ruff check .
python -m ruff format --check .
python -m pytest
python scripts/check_examples.py
python -m build
```

On Windows, use `.venv\Scripts\Activate.ps1` and `$env:MPLBACKEND = "Agg"` in PowerShell.
The noninteractive backend also allows dashboard plots in worker threads on macOS.
This standard setup
covers ordinary research workflows and matches CI's full profile. Examples use synthetic
data by default; the runner excludes the download example and uses a noninteractive plotting
backend. It does not exercise neural/Prophet flags or launch the dashboard.

To verify the small core dependency set, use a **separate fresh environment** and run:

```bash
python -m pip install . pytest
python -m pytest
```

Optional-dependency skips are expected in this core profile. The standard profile still
skips neural, Prophet and dashboard tests unless their packages are installed. Pytest prints
skip reasons: a passing run establishes only the coverage actually executed, and example
execution alone does not establish numerical correctness.

For changes involving heavy models or the dashboard, add their dependencies and checks:

```bash
python -m pip install -e '.[models,neural,prophet,apps,reports,sentiment,dev]'
export MPLBACKEND=Agg
python -m pytest tests/test_research_models_reports.py tests/test_app.py
python examples/research_models.py --neural --prophet
```

CI runs core and standard profiles on Python 3.12–3.14, plus heavy-model and dashboard tests
on Python 3.12. See the [workflow](.github/workflows/ci.yml) for exact environments.

### Live providers

Network tests are skipped unless explicitly enabled. With the standard dependencies:

```bash
python -m pytest --live -m integration
python scripts/check_examples.py --live
```

These contact public providers and can fail because of throttling or schema changes. They
are separate from offline CI and do not establish ongoing availability. See
[provider contracts](docs/providers.md) and [research workflows](docs/workflows.md) for
source limitations and account-dependent integrations.

Include focused regression coverage when changing numerical results, signal timing or
execution accounting. Use hand-calculated fixtures or independent references where practical.
In a PR, explain the resulting behavior, the checks run and any skipped or unverified paths.
