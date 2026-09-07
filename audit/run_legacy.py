"""Run original scripts with bounded runtime; never run order/notification/browser code."""

import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from _legacy import export_legacy

ROOT = Path(__file__).resolve().parents[1]
LEGACY_SOURCE = ROOT
UNSAFE = {
    "price_alert_email",
    "robinhood_bot",
    "deep_learning_bot",
    "stock_data_sms",
    "stock_twilio_server",
    "send_top_movers",
    "tradingview_signals",
    "tradingview_intraday_data",
    "tradingview_recommendations",
    "main_indicators_streamlit",
}


def run(record):
    path = record["path"]
    if Path(path).stem in UNSAFE:
        return {
            "path": path,
            "status": "Not executed: external messages/orders, browser or server side effects; reviewed source",
        }
    if not record["lines"]:
        return {"path": path, "status": "Empty package marker"}
    with tempfile.TemporaryDirectory(prefix="finance-legacy-") as folder:
        shutil.copytree(LEGACY_SOURCE, folder, dirs_exist_ok=True)
        env = {
            k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "TMPDIR", "SSL_CERT_FILE")
        }
        env.update(
            MPLBACKEND="Agg",
            MPLCONFIGDIR=folder,
            PYTHONPATH=folder,
            OPENBLAS_NUM_THREADS="1",
            OMP_NUM_THREADS="1",
        )
        started = time.monotonic()
        try:
            result = subprocess.run(
                [sys.executable, str(Path(folder) / path)],
                cwd=folder,
                env=env,
                input="AAPL\n2\n5\n10\nquit\n",
                text=True,
                capture_output=True,
                timeout=12,
            )
            output = (result.stdout + "\n" + result.stderr).strip()
            status = (
                "Exited 0; output requires inspection"
                if result.returncode == 0
                else output.splitlines()[-1]
            )
            return {
                "path": path,
                "status": status,
                "returncode": result.returncode,
                "seconds": round(time.monotonic() - started, 2),
                "output": output[-2500:],
            }
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or b"") + (exc.stderr or b"")
            return {
                "path": path,
                "status": "Timeout after 12 seconds",
                "output": output.decode(errors="replace")[-2500:],
            }


if __name__ == "__main__":
    inventory = json.loads((ROOT / "audit/inventory.json").read_text())
    with tempfile.TemporaryDirectory(prefix="finance-v1-source-") as source:
        LEGACY_SOURCE = Path(source)
        export_legacy(LEGACY_SOURCE)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(run, inventory))
    (ROOT / "audit/legacy_runs.json").write_text(json.dumps(results, indent=2) + "\n")
    from collections import Counter

    print(Counter(r["status"] for r in results))
