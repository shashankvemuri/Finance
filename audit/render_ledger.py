"""Render per-file decisions with preserved execution and verification evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "12dac57c7f62146f7073ccc17f64bc45fd687b5d"


def main():
    inventory = json.loads((ROOT / "audit/inventory.json").read_text())
    decisions = json.loads((ROOT / "audit/dispositions.json").read_text())
    runs = {r["path"]: r for r in json.loads((ROOT / "audit/legacy_runs.json").read_text())}
    diagnostics = {
        r["path"]: r for r in json.loads((ROOT / "audit/diagnostic_runs.json").read_text())
    }
    assert {r["path"] for r in inventory} == set(decisions) == set(runs)
    head = f"""# Finance v2 migration ledger

Legacy baseline: `{BASELINE}`. All 183 original Python files were inventoried before deletion.
Original sources remain available with `git show {BASELINE}:<old-path>`.

Direct executions used Python 3.12 and current dependencies, real network requests, a temporary
working directory and bounded runtime. Inputs, exclusions and error tails are preserved in
[audit/legacy_runs.json](audit/legacy_runs.json). Missing optional dependencies are recorded as
blocked executions, not proof that the underlying concept is invalid. Ten message/order/browser/server
entry points were source-reviewed without invoking external side effects.

The second indicator pass used **real 2023–2024 cached bars and downloader compatibility shims**;
these are diagnostic runs, not unmodified successes. It completed 71 of 82 scripts. Results, shapes,
columns, final values and failures are in [audit/diagnostic_runs.json](audit/diagnostic_runs.json).
A successful exit was inspected: several legacy scrapers printed error tables or empty outputs while
exiting zero. The dividend calendar, pivot calculator and intraday example actually produced data.

Replacement verification: [tests](tests), [live execution report](audit/live_verification.json),
[offline examples](audit/examples_offline.json), [live examples](audit/examples_live.json),
and [methodology](docs/methodology.md). Pure numerical tests include independent `ta` comparisons,
published RSI values, analytical optimizer solutions, direct accounting and stochastic moments.
Data examples require explicit optional dependencies. No historical vendor rankings or neural
prediction claims are retained merely because code once trained.

| Old path | Concepts / intended purpose | Current execution status | v2 destination | Decision | Reason / correction | Replacement verification |
| --- | --- | --- | --- | --- | --- | --- |
"""
    for record in inventory:
        path = record["path"]
        decision = decisions[path]
        run = runs[path]
        status = run["status"]
        if path == "tickers.py":
            status = "Definitions loaded only; not a functioning universe download. Calls relied on outdated HTML/CSVs."
        elif status.startswith("Exited 0"):
            if path in [
                "stock_data/get_dividend_calendar.py",
                "stock_data/pivots_calculator.py",
                "stock_data/yf_intraday_data.py",
            ]:
                status = (
                    "Executed and inspected: "
                    + {
                        "stock_data/get_dividend_calendar.py": "608 calendar rows; numeric rates sorted as strings",
                        "stock_data/pivots_calculator.py": "daily pivot table and intraday chart input",
                        "stock_data/yf_intraday_data.py": "NKE minute OHLCV with positive prices/volumes",
                    }[path]
                )
            else:
                status = "Exit 0 but output is an error/empty table; raw HTML treated as path by pandas.read_html"
        if len(status) > 220:
            status = status[:180] + "… (full evidence in legacy_runs.json)"
        if path in diagnostics:
            status += "; diagnostic: " + diagnostics[path]["status"]
        if decision["decision"] == "remove" and decision["destination"].startswith("None"):
            verification = (
                "Source reviewed; explicit scope rejection. No unsupported replacement claimed."
            )
        else:
            area = path.split("/")[0]
            verification = {
                "technical_indicators": "test_indicators.py / test_additional_contracts.py: formulas, independent references, prefix causality; live indicator outputs",
                "stock_analysis": "test_analytics.py / test_additional_contracts.py / test_backtesting.py; live CAPM, valuation, CFTC, sentiment and examples",
                "find_stocks": "test_data_screening.py / test_provider_contracts.py; live small-universe diagnostics and company/news snapshots",
                "portfolio_strategies": "test_backtesting.py / test_portfolio.py / test_models.py; live fill reconciliation, constraints, stochastic moments and examples",
                "machine_learning": "test_models.py / test_additional_contracts.py; live chronological baseline metrics and structure invariants",
                "stock_data": "test_provider_contracts.py / test_data_screening.py / test_indicators.py; 10 live provider workflows and examples",
            }.get(
                area,
                "Package imports, indicator tests, provider normalization and live universe workflows",
            )
        values = [
            f"`{path}`",
            decision["concept"],
            status,
            decision["destination"],
            decision["decision"],
            decision["reason"],
            verification,
        ]
        head += (
            "| " + " | ".join(str(v).replace("|", "/").replace("\n", " ") for v in values) + " |\n"
        )
    head += """
## Non-Python assets and dependency disposition

- `chromedriver`: remove the 15 MB platform browser binary; v2 has no browser dependency.
- `amex_tickers.csv`, `nasdaq_tickers.csv`, `nyse_tickers.csv`, `russell3000_tickers.csv`,
  `s&p500_tickers.csv`: remove stale universe snapshots. Nasdaq Trader and S&P500 adapters provide
  dated current data. Historical point-in-time index membership and licensed Russell membership are
  intentionally outside supported scope; current constituents must not be used as historical truth.
- `requirements.txt`: replace 46 globally pinned packages with two core dependencies and optional extras.
- Original MIT license and technical-indicator provenance acknowledgement retained.

## Deliberate scope decisions

- Preserve the original trading/statistical ideas through canonical implementations, not old filenames.
- Price/time angle prediction has no defined units or validated method in the Gann script; remove it.
- Preserve Astral Timing's actual lagged price comparisons as an explicitly experimental `lag_reversal`.
- Preserve Green Line confirmation, technical votes, transcript/news sentiment, probabilistic direction,
  cointegration, Gaussian mixture and anomaly experiments; no profitability claims.
- Remove live brokerage, delivery servers, social crawling and opaque vendor widgets. Their numerical
  inputs/outputs remain composable. Do not introduce dormant integrations with unverified credentials.
- Neural forecasting remains an MLP/lag-feature experiment. Separate LSTM/CNN and Prophet dependency
  stacks do not earn supported status from their historical training fits. A future implementation
  needs a defensible chronological benchmark and incremental value over the retained experiments.
- Replace perfect intrabar stops with explicitly delayed close-based stops. Tick execution, margin,
  institutional order types and market impact are outside this modest engine's scope.
- Market-wide earnings aggregation, full statement/transcript acquisition, historical universes and
  exchange-wide breadth feeds need separately maintained provider contracts; supplied-input calculations
  and per-company earnings/news/fundamentals remain supported.
"""
    (ROOT / "MIGRATION.md").write_text(head)
    print(f"Rendered {len(inventory)} explicit dispositions")


if __name__ == "__main__":
    main()
