"""Run example entry points; network access requires --live."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="use real provider data")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    failures = 0
    for path in sorted((root / "examples").glob("*.py")):
        if path.name.startswith("_") or (not args.live and path.name == "download_market_data.py"):
            continue
        command = [sys.executable, str(path)] + (["--live"] if args.live else [])
        print(f"Running {path.name}", flush=True)
        try:
            result = subprocess.run(
                command,
                cwd=root,
                env=dict(os.environ, MPLBACKEND="Agg"),
                timeout=90,
                check=False,
            )
        except subprocess.TimeoutExpired:
            print(f"Timed out: {path.name}", file=sys.stderr)
            failures += 1
        else:
            failures += result.returncode != 0
    if failures:
        raise SystemExit(f"{failures} example(s) failed")


if __name__ == "__main__":
    main()
