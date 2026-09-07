"""Second-pass legacy diagnostics using real cached bars, without editing the original source.

Only obsolete downloader entry points are shimmed. Fixed 2023-2024 bars replace each
requested horizon so downstream formulas can execute repeatably. This is NOT an
unmodified legacy success. Main audit/run_legacy.py records the direct executions.
"""

import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from _legacy import export_legacy

ROOT = Path(__file__).resolve().parents[1]


def child(path, fixture_dir):
    import runpy

    import numpy as np
    import pandas as pd
    import pandas_datareader.data as pdr
    import yfinance as yf

    def download(ticker, *args, **kwargs):
        file = Path(fixture_dir) / (str(ticker).replace("^", "INDEX_") + ".csv")
        if not file.exists():
            raise ValueError(f"No real diagnostic fixture for {ticker}")
        return pd.read_csv(file, index_col=0, parse_dates=True)

    yf.pdr_override = lambda: None
    yf.download = download
    pdr.get_data_yahoo = download
    state = runpy.run_path(str(Path(fixture_dir) / "legacy" / path), run_name="__main__")
    report = {}
    for key in ["df", "dataset", "df1"]:
        data = state.get(key)
        if isinstance(data, pd.DataFrame):
            numeric = data.select_dtypes(include="number")
            report[key] = {
                "shape": list(data.shape),
                "columns": list(data.columns),
                "infinite_values": int(np.isinf(numeric.to_numpy()).sum()),
                "last": {str(k): float(v) for k, v in numeric.iloc[-1].items()},
            }
    print("DIAGNOSTIC_OUTPUT " + json.dumps(report, allow_nan=True))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        child(sys.argv[1], sys.argv[2])
    else:
        import yfinance as yf

        with tempfile.TemporaryDirectory(prefix="finance-diagnostic-") as folder:
            export_legacy(Path(folder) / "legacy")
            for ticker in ["AAPL", "QQQ", "SPY", "^GSPC", "META", "CRON", "RIG", "AMD", "NIO"]:
                data = yf.Ticker(ticker).history(
                    start="2023-01-01",
                    end="2025-01-01",
                    auto_adjust=False,
                    timeout=15,
                    raise_errors=True,
                )
                if data.empty:
                    raise ValueError(f"Empty live fixture for {ticker}")
                data.index = data.index.tz_localize(None)
                data.index.name = "Date"
                data = data[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
                data.to_csv(Path(folder) / (ticker.replace("^", "INDEX_") + ".csv"))

            def run(path):
                env = dict(
                    os.environ,
                    MPLBACKEND="Agg",
                    PYTHONPATH=str(Path(folder) / "legacy"),
                    MPLCONFIGDIR=folder,
                    OPENBLAS_NUM_THREADS="1",
                    OMP_NUM_THREADS="1",
                )
                try:
                    result = subprocess.run(
                        [sys.executable, __file__, str(path.relative_to(ROOT)), folder],
                        cwd=folder,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    output = result.stdout + result.stderr
                    evidence = next(
                        (
                            line.removeprefix("DIAGNOSTIC_OUTPUT ")
                            for line in result.stdout.splitlines()
                            if line.startswith("DIAGNOSTIC_OUTPUT ")
                        ),
                        None,
                    )
                    return {
                        "path": str(path.relative_to(ROOT)),
                        "returncode": result.returncode,
                        "status": "Fixture-backed execution completed"
                        if result.returncode == 0
                        else output.strip().splitlines()[-1],
                        "result": json.loads(evidence) if evidence else None,
                        "output_tail": output[-500:],
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "path": str(path.relative_to(ROOT)),
                        "status": "20 second diagnostic timeout",
                    }

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
                results = list(
                    pool.map(
                        run,
                        [
                            ROOT / item["path"]
                            for item in json.loads((ROOT / "audit/inventory.json").read_text())
                            if item["path"].startswith("technical_indicators/")
                        ],
                    )
                )
            (ROOT / "audit/diagnostic_runs.json").write_text(json.dumps(results, indent=2) + "\n")
            from collections import Counter

            print(Counter(r["status"] for r in results))
