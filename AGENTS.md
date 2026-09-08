# Working in Finance

Finance is a Python quantitative research toolkit. Keep code and examples approachable
to human contributors as well as coding agents.

## Start here

- [README](README.md): installation and public usage.
- [Contributing](CONTRIBUTING.md): task map, dependency profiles and verification commands.
- [Provider contracts](docs/providers.md): data sources, units and availability limits.
- [Research workflows](docs/workflows.md): composed examples and optional features.

## Find the right boundary

Public imports are exposed by each `src/finance/<area>/__init__.py`.
`data` owns acquisition and normalization; `indicators`, `analytics`, `screening` and
`portfolio` own calculations. `strategies` produces targets, `backtesting` executes them,
and `models` owns statistical experiments. Presentation belongs in `reports`, `examples`
or `apps`; external actions belong in `integrations`.

Read the closest implementation, runnable example and focused test before editing.
Prefer small functions and existing boundaries over new frameworks. Keep optional imports
inside the features that need them; importing core modules must not fetch data or start work.

## Preserve financial meaning

- Check each API's units: a return of `0.05` means 5%, while RSI uses 0–100.
- Preserve index alignment and indicator warm-up NaNs. Do not silently fill missing prices.
- Keep all OHLC prices on the same adjustment basis. Adjusted prices already include
  dividend effects; adding dividend cash again would double-count them.
- Strategies use information available at the signal timestamp. The backtester applies
  the execution delay; do not shift strategy targets a second time.
- Current universes and company snapshots cannot establish historical availability.
  Inspect provider completeness metadata and batch errors before using a result.
- Evaluate forecasts chronologically, fit transformations on training data and retain a
  simple baseline. Training fit is not evidence of predictive advantage.

## Finish a change

Use the relevant checks in [Contributing](CONTRIBUTING.md#verification). Numerical changes
need a focused regression test and an independent formula, fixture or reference where
practical. Inspect example outputs as well as exit status. Report the commands run, skipped
coverage and any provider failures accurately. Keep documentation about current behavior;
put API assumptions in short docstrings and usage in runnable examples.
