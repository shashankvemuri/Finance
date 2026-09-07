# v2 verification evidence

`inventory.json` enumerates all 183 original Python files. `dispositions.json` records
reviewed concepts and decisions; `render_ledger.py` produces the root migration ledger.
`legacy_runs_initial.json` preserves the initial direct run (isolated working directories).
`legacy_runs.json` is the final direct run, with original Python and ticker CSV files
materialized together in a fresh temporary directory for each program. This prevents a
changed working directory from creating false missing-static-file diagnoses.

`diagnostic_runs.json` is a different experiment: the 82 old indicator scripts receive real
cached 2023–2024 bars through explicit downloader compatibility shims. 71 completed. It
exposes downstream errors but does not establish unmodified legacy compatibility.
`provider_probes.json` is preliminary evidence, including schema failures fixed later.
`live_verification.json` is the authoritative final successful integration run.

`examples_offline.json` and `examples_live.json` preserve example stdout/stderr. Most examples
use seeded synthetic bars by default; `--live` uses Yahoo. The download example always uses
the network. `verification_environment.txt` records installed versions, not an installation
lockfile; it includes extra packages used only to diagnose legacy scripts.

Reproduce pure tests with `python -m pytest`. Reproduce live checks using
`python audit/verify_live.py` and `python audit/run_examples.py --live` after installing
`.[data,portfolio,models,sentiment,plot,dev]`. Historical daily dates are fixed; intraday dates
must be updated when the provider retention window advances. Results may change with vendor
revisions. Some provider payloads contain legitimate missing values; undefined statistics
are not replaced with fabricated zeros.

Legacy audit scripts recover baseline `12dac57` from Git, without changing the current
branch or restoring browser binaries. Run `python audit/run_legacy.py` for direct executions
or `python audit/diagnose_indicators.py` for fixture-backed diagnostics. They additionally
need the original programs' optional packages; the recorded environment includes
pandas-datareader, matplotlib, seaborn and mplfinance. Credential/order/notification/browser
entry points are deliberately not invoked. First-stage dependency failures remain valid
observations, not evidence against the financial idea itself.
