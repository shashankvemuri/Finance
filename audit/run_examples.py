"""Execute example entry points, keeping provider calls explicit with --live."""

import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    live = "--live" in sys.argv
    results = []
    for path in sorted((root / "examples").glob("*.py")):
        if path.name.startswith("_") or (not live and path.name == "download_market_data.py"):
            continue
        command = [sys.executable, str(path)] + (["--live"] if live else [])
        result = subprocess.run(
            command,
            cwd=root,
            env=dict(os.environ, MPLBACKEND="Agg"),
            capture_output=True,
            text=True,
            timeout=90,
        )
        results.append(
            {
                "example": path.name,
                "exit_code": result.returncode,
                "output": result.stdout[-3500:],
                "stderr": result.stderr[-1000:],
            }
        )
        print(path.name, result.returncode, flush=True)
    suffix = "live" if live else "offline"
    (root / "audit" / f"examples_{suffix}.json").write_text(json.dumps(results, indent=2) + "\n")
    if any(r["exit_code"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
