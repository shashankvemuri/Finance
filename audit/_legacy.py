"""Materialize the audited source from Git without changing the working branch."""

import io
import json
import subprocess
import tarfile
from pathlib import Path

BASELINE = "12dac57"
ROOT = Path(__file__).resolve().parents[1]


def export_legacy(destination: Path) -> None:
    paths = [item["path"] for item in json.loads((ROOT / "audit/inventory.json").read_text())]
    paths += [
        "amex_tickers.csv",
        "nasdaq_tickers.csv",
        "nyse_tickers.csv",
        "russell3000_tickers.csv",
        "s&p500_tickers.csv",
    ]
    archive = subprocess.check_output(["git", "archive", BASELINE, *paths], cwd=ROOT)
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(destination, filter="data")
