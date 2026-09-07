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
