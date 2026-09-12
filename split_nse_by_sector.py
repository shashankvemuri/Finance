"""
split_nse_by_sector.py
======================
Reads Nse_tickers.csv, fetches the sector for each ticker from Yahoo Finance
(with crumb auth + rate limiting), and writes one CSV per sector into nse_sectors/.

Usage:
    python split_nse_by_sector.py

Output:
    nse_sectors/Technology.csv
    nse_sectors/Financial Services.csv
    ...
    nse_sectors/Unknown.csv      ← delisted / no sector returned
    nse_sectors/_master.csv      ← full table with Symbol + Sector columns
"""

import os
import ssl
import time
import urllib.request
import warnings

import pandas as pd
import urllib3
from curl_cffi import requests as curl_requests

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

_sys_proxies = urllib.request.getproxies()
_YF_SUMMARY = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
_YF_CRUMB   = "https://query2.finance.yahoo.com/v1/test/getcrumb"


def _make_session():
    s = curl_requests.Session(impersonate="chrome110", verify=False, proxies=_sys_proxies or {})
    s.get("https://finance.yahoo.com", timeout=15)
    crumb = s.get(_YF_CRUMB, timeout=10).text.strip()
    return s, crumb


# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
CSV_IN   = os.path.join(BASE_DIR, "Nse_tickers.csv")
OUT_DIR  = os.path.join(BASE_DIR, "nse_sectors")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load tickers ──────────────────────────────────────────────────────────────
raw     = pd.read_csv(CSV_IN)
symbols = raw.iloc[:, 0].dropna().str.strip().tolist()
symbols = [s.replace(".NS", "") for s in symbols]

print("Initialising Yahoo Finance session (fetching crumb) ...")
session, crumb = _make_session()
print(f"Crumb obtained: {crumb}\n")


def get_sector(symbol: str) -> tuple:
    """Return (sector, industry) for the given NSE symbol."""
    url = _YF_SUMMARY.format(ticker=f"{symbol}.NS")
    params = {"modules": "summaryProfile,assetProfile", "crumb": crumb}
    try:
        r = session.get(url, params=params, timeout=15)
        data = r.json()
        result = data["quoteSummary"]["result"]
        if not result:
            return "Unknown", "Unknown"
        merged = {}
        for mod in result:
            for section in mod.values():
                if isinstance(section, dict):
                    for k, v in section.items():
                        merged[k] = v["raw"] if isinstance(v, dict) and "raw" in v else v
        sector   = merged.get("sector")   or "Unknown"
        industry = merged.get("industry") or "Unknown"
        return sector, industry
    except Exception:
        return "Unknown", "Unknown"


# ── Fetch sectors with rate limiting ─────────────────────────────────────────
print(f"Fetching sector for {len(symbols)} tickers (1.5 s gap) ...\n")

rows = []
for i, sym in enumerate(symbols, 1):
    sector, industry = get_sector(sym)
    rows.append({"Symbol": sym, "YF_Ticker": f"{sym}.NS", "Sector": sector, "Industry": industry})
    icon = "✔" if sector != "Unknown" else "⚠"
    print(f"  [{i:>3}/{len(symbols)}] {sym:<18} → {sector:<30} {icon}")
    time.sleep(1.5)

master_df = pd.DataFrame(rows)

# ── Save master CSV ───────────────────────────────────────────────────────────
master_path = os.path.join(OUT_DIR, "_master.csv")
master_df.to_csv(master_path, index=False)
print(f"\nMaster file → {master_path}")

# ── Split and save per-sector CSVs ────────────────────────────────────────────
print("\nWriting sector CSVs:")
for sector, group in master_df.groupby("Sector"):
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in sector).strip()
    path = os.path.join(OUT_DIR, f"{safe_name}.csv")
    group[["Symbol"]].to_csv(path, index=False)
    print(f"  {sector:<35} {len(group):>3} tickers  →  {os.path.basename(path)}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "─" * 60)
counts = master_df.groupby("Sector").size().sort_values(ascending=False)
for s, n in counts.items():
    print(f"  {s:<35} {n:>3}")
print("─" * 60)
print(f"  {'TOTAL':<35} {counts.sum():>3}\n")
print("Run the analyzer on a specific sector:")
print("  from nse_stock_analyzer import NSEStockAnalyzer")
print("  NSEStockAnalyzer(csv_path='nse_sectors/Technology.csv').analyze()")

