# Contributing

Keep calculations separate from data providers. Include a focused regression test for
changes to numerical results, signal timing or execution accounting. Prefer hand-calculated
fixtures or independent references for financial formulas.

Install the development dependencies and run the local checks:

```bash
python -m pip install -e '.[data,portfolio,models,sentiment,plot,dev]'
ruff check .
ruff format --check .
python -m pytest
python scripts/check_examples.py
```

Tests and examples use offline data by default. To check external providers explicitly:

```bash
python -m pytest --live -m integration
python scripts/check_examples.py --live
```

CI checks core and optional features on Python 3.12–3.14 without live provider requests.
