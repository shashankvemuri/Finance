"""Discover growth stocks, explain the screen and optionally export a report. Add --live for Finviz."""

import argparse
from pathlib import Path

import pandas as pd

from finance.data import Finviz, fetch_many
from finance.reports import export_table, research_report
from finance.screening import growth_screen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.live:
        provider = Finviz()
        discovery = provider.screen(["cap_largeover", "fa_epsqoq_o10"], limit=20)
        batch = fetch_many(discovery.index, provider.company)
        if not batch.errors.empty:
            print("Provider failures:", batch.errors.to_string())
        if not batch.data:
            raise RuntimeError("No company snapshots available")
        companies = batch.table()
        companies.attrs = discovery.attrs
        print(f"Examining {len(companies)} of {discovery.attrs['total_matches']} matches")
    else:
        print("Synthetic company inputs; use --live for public Finviz snapshots.")
        companies = pd.DataFrame(
            {
                "earnings_growth": [0.2, 0.04, 0.3],
                "revenue_growth": [0.15, 0.1, 0.2],
                "profit_margin": [0.2, 0.12, 0.15],
                "institutional_transactions": [0.03, 0.01, -0.02],
                "pe": [25, 30, 35],
            },
            index=["ALPHA", "BETA", "GAMMA"],
        )
    result = growth_screen(companies)
    print(
        result[["earnings_growth", "revenue_growth", "profit_margin", "pe", "passed"]].to_string()
    )
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        export_table(result, args.output / "watchlist.csv")
        research_report({"Growth screen": result}, args.output / "watchlist.html")


if __name__ == "__main__":
    main()
