"""
NSE Stock Analyzer
==================
Reads tickers from Nse_tickers.csv and produces a comprehensive analysis report:
  - BUY / SELL / HOLD recommendation
  - Sector & geopolitical / government-policy impact
  - Technical analysis (RSI, MACD, Bollinger Bands, SMA/EMA, ATR)
  - Fundamental analysis (P/E, EPS, Beta, Market Cap, Debt/Equity)
  - CAPM: Beta, Alpha, Expected Return vs NIFTY 50
  - Kelly Criterion: optimal position size
  - Entry price, Target (exit), Stop-Loss with Risk/Reward ratio
  - Backtest results (SMA-20/50 crossover)
  - Monte Carlo 30-day price range
  - Recommended holding duration
"""

import os
import sys
import ssl
import time
import warnings
import datetime as dt

import numpy as np
import pandas as pd
import urllib3
import yfinance as yf
import urllib.request
from curl_cffi import requests as curl_requests

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── SSL bypass ────────────────────────────────────────────────────────────────
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
ssl._create_default_https_context = ssl._create_unverified_context

_sys_proxies = urllib.request.getproxies()

_YF_CHART   = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
_YF_SUMMARY = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
_YF_CRUMB   = "https://query2.finance.yahoo.com/v1/test/getcrumb"
_YF_MODULES = (
    "summaryProfile,assetProfile,financialData,"
    "defaultKeyStatistics,summaryDetail,price"
)


def _get_session() -> tuple:
    """
    Create a curl_cffi Chrome session, warm it with a Yahoo Finance visit,
    and fetch the crumb token required by quoteSummary API.
    Returns (session, crumb).
    """
    s = curl_requests.Session(
        impersonate="chrome110",
        verify=False,
        proxies=_sys_proxies or {},
    )
    try:
        s.get("https://finance.yahoo.com", timeout=15)
        crumb = s.get(_YF_CRUMB, timeout=10).text.strip()
    except Exception:
        crumb = ""
    return s, crumb


_session, _crumb = _get_session()


def _yf_download_with_retry(ticker: str, start, end, max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch OHLCV directly from Yahoo Finance chart API via curl_cffi.
    Bypasses yf.download's internal guce.yahoo.com consent flow entirely.
    """
    start_ts = int(pd.Timestamp(start).timestamp())
    end_ts   = int(pd.Timestamp(end).timestamp())
    url = _YF_CHART.format(ticker=ticker)
    params = {
        "period1": start_ts,
        "period2": end_ts,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }
    global _session, _crumb
    for attempt in range(1, max_retries + 1):
        try:
            r = _session.get(url, params=params, timeout=20)
            data = r.json()
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            ohlcv = result["indicators"]["quote"][0]
            adj = (
                result["indicators"]
                .get("adjclose", [{}])[0]
                .get("adjclose", ohlcv["close"])
            )
            idx = pd.to_datetime(timestamps, unit="s", utc=True).tz_localize(None)
            df = pd.DataFrame(
                {
                    "Open":      ohlcv["open"],
                    "High":      ohlcv["high"],
                    "Low":       ohlcv["low"],
                    "Close":     ohlcv["close"],
                    "Adj Close": adj,
                    "Volume":    ohlcv["volume"],
                },
                index=idx,
            )
            df.index.name = "Date"
            df = df.dropna(subset=["Close"])
            if not df.empty:
                return df
        except Exception:
            pass
        _session, _crumb = _get_session()
        time.sleep(2 ** attempt)
    return pd.DataFrame()


def _yf_info_with_retry(ticker: str, max_retries: int = 3) -> dict:
    """
    Fetch stock fundamentals directly from Yahoo Finance quoteSummary API.
    Uses the crumb token obtained during session initialisation.
    """
    url = _YF_SUMMARY.format(ticker=ticker)
    global _session, _crumb
    for attempt in range(1, max_retries + 1):
        try:
            params = {"modules": _YF_MODULES, "crumb": _crumb}
            r = _session.get(url, params=params, timeout=20)
            data = r.json()
            modules = data["quoteSummary"]["result"]
            if not modules:
                raise ValueError("empty modules")
            merged: dict = {}
            for mod in modules:
                for section in mod.values():
                    if isinstance(section, dict):
                        for k, v in section.items():
                            # Yahoo wraps values: {"raw": x, "fmt": "y"} — unwrap
                            if isinstance(v, dict) and "raw" in v:
                                merged[k] = v["raw"]
                            elif not isinstance(v, dict):
                                merged[k] = v
            if len(merged) > 5:
                return merged
        except Exception:
            pass
        _session, _crumb = _get_session()
        time.sleep(2 ** attempt)
    return {}

# ─────────────────────────────────────────────────────────────────────────────
# Sector → Geopolitical / Government Policy impact mapping (India context)
# ─────────────────────────────────────────────────────────────────────────────
SECTOR_IMPACT = {
    "Technology": (
        "USD/INR exchange rate, US tech-spend cycles, H-1B visa policy, "
        "India IT export incentives, data-localisation regulations, US recession risk."
    ),
    "Financial Services": (
        "RBI repo-rate decisions, CRR/SLR changes, NPA norms, SEBI regulations, "
        "credit-growth outlook, government bank-recapitalisation plans."
    ),
    "Healthcare": (
        "USFDA compliance & drug approvals, PLI for pharma, drug-price control orders (DPCO), "
        "export restrictions, global API supply chains, patent cliffs."
    ),
    "Energy": (
        "Crude-oil & natural-gas prices, OPEC+ policy, government fuel-price policy, "
        "green-energy transition targets, coal-block auctions, subsidy regime."
    ),
    "Consumer Defensive": (
        "Rural demand & monsoon, CPI inflation, GST council rate changes, "
        "FMCG price controls, MNREGA spending, government welfare schemes."
    ),
    "Consumer Cyclical": (
        "Disposable income & credit growth, EV transition PLI, fuel prices, "
        "import duties on components, government capex spillover."
    ),
    "Industrials": (
        "Government capex & infrastructure spend, PLI schemes, Defence indigenisation, "
        "Make-in-India policy, global supply-chain shifts, logistics costs."
    ),
    "Basic Materials": (
        "China steel/aluminium demand, commodity-cycle, import duties, "
        "mining allocation policy, global trade tariffs, INR movement."
    ),
    "Real Estate": (
        "RBI interest-rate cycle, RERA compliance, affordable-housing policy, "
        "stamp-duty incentives, government infrastructure investment."
    ),
    "Communication Services": (
        "5G spectrum auctions, AGR dues resolution, FDI limits in telecom, "
        "OTT regulation, data-privacy laws, government digitisation push."
    ),
    "Utilities": (
        "Government electricity tariff policy, renewable-energy targets, "
        "coal-linkage availability, DISCOM health, green-hydrogen push."
    ),
    "Unknown": (
        "General macro factors: RBI monetary policy, Union Budget, global risk-off, "
        "INR/USD, FII flows, crude-oil prices."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Helper: simple RSI
# ─────────────────────────────────────────────────────────────────────────────
def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


# ─────────────────────────────────────────────────────────────────────────────
# Main class
# ─────────────────────────────────────────────────────────────────────────────
class NSEStockAnalyzer:
    """
    End-to-end NSE stock analysis engine.

    Parameters
    ----------
    csv_path : str
        Path to Nse_tickers.csv  (one symbol per row, column header 'Symbol').
    lookback_years : int
        Years of historical data to download (default 2).
    nifty_ticker : str
        Yahoo Finance ticker for the benchmark index (default '^NSEI').
    risk_free_rate : float
        Annual risk-free rate fraction (default 0.065 = 6.5 % India 10-yr Gsec).
    monte_carlo_sims : int
        Number of Monte Carlo simulation paths (default 500).
    """

    NIFTY = "^NSEI"

    def __init__(
        self,
        csv_path: str = None,
        lookback_years: int = 2,
        nifty_ticker: str = "^NSEI",
        risk_free_rate: float = 0.065,
        monte_carlo_sims: int = 500,
    ):
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(__file__), "Nse_tickers.csv")

        self.csv_path = csv_path
        self.lookback_years = lookback_years
        self.nifty_ticker = nifty_ticker
        self.risk_free_rate = risk_free_rate
        self.monte_carlo_sims = monte_carlo_sims

        self.end = dt.date.today()
        self.start = self.end - dt.timedelta(days=int(365.25 * lookback_years))

        self.tickers = self._load_tickers()
        self._nifty_df = None  # lazy-loaded

    # ── Ticker loading ────────────────────────────────────────────────────────

    def _load_tickers(self) -> list:
        df = pd.read_csv(self.csv_path)
        col = df.columns[0]
        symbols = df[col].dropna().str.strip().tolist()
        # Append .NS suffix for Yahoo Finance (NSE India)
        return [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]

    # ── Data download ─────────────────────────────────────────────────────────

    def _download(self, ticker: str) -> pd.DataFrame:
        df = _yf_download_with_retry(ticker, self.start, self.end)
        if df is None or df.empty:
            raise ValueError(f"No data returned for {ticker} \u2014 may be delisted or ticker incorrect")
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    def _nifty_data(self) -> pd.DataFrame:
        if self._nifty_df is None:
            self._nifty_df = self._download(self.nifty_ticker)
        return self._nifty_df

    # ── Technical analysis ────────────────────────────────────────────────────

    def _technicals(self, df: pd.DataFrame) -> dict:
        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        vol = df["Volume"]

        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        sma150 = close.rolling(150).mean()
        sma200 = close.rolling(200).mean()
        ema20 = close.ewm(span=20, adjust=False).mean()

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - signal_line

        # Bollinger Bands (20-period, 2σ)
        bb_mid = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_upper = bb_mid + 2 * bb_std
        bb_lower = bb_mid - 2 * bb_std

        # ATR (14-period)
        tr = pd.concat(
            [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1
        ).max(axis=1)
        atr = tr.rolling(14).mean()

        # RSI
        rsi = _rsi(close, 14)

        # 52-week high/low
        w52_high = high.rolling(252).max()
        w52_low = low.rolling(252).min()

        last = -1  # last valid index
        return {
            "close": round(float(close.iloc[last]), 2),
            "sma20": round(float(sma20.iloc[last]), 2),
            "sma50": round(float(sma50.iloc[last]), 2),
            "sma150": round(float(sma150.iloc[last]) if not pd.isna(sma150.iloc[last]) else 0, 2),
            "sma200": round(float(sma200.iloc[last]) if not pd.isna(sma200.iloc[last]) else 0, 2),
            "ema20": round(float(ema20.iloc[last]), 2),
            "rsi": round(float(rsi.iloc[last]), 2),
            "macd": round(float(macd.iloc[last]), 4),
            "macd_signal": round(float(signal_line.iloc[last]), 4),
            "macd_hist": round(float(macd_hist.iloc[last]), 4),
            "bb_upper": round(float(bb_upper.iloc[last]), 2),
            "bb_mid": round(float(bb_mid.iloc[last]), 2),
            "bb_lower": round(float(bb_lower.iloc[last]), 2),
            "atr": round(float(atr.iloc[last]), 2),
            "52w_high": round(float(w52_high.iloc[last]) if not pd.isna(w52_high.iloc[last]) else 0, 2),
            "52w_low": round(float(w52_low.iloc[last]) if not pd.isna(w52_low.iloc[last]) else 0, 2),
            "vol_avg20": int(vol.rolling(20).mean().iloc[last]),
        }

    # ── Minervini trend-template check ───────────────────────────────────────

    def _minervini_check(self, t: dict) -> dict:
        c = t["close"]
        passed = []
        failed = []

        checks = {
            "Price > SMA150 > SMA200": c > t["sma150"] > t["sma200"] and t["sma150"] > 0,
            "Price > SMA50": c > t["sma50"],
            "Price ≥ 1.3× 52w Low": c >= 1.3 * t["52w_low"] if t["52w_low"] > 0 else False,
            "Price ≥ 0.75× 52w High": c >= 0.75 * t["52w_high"] if t["52w_high"] > 0 else False,
        }
        for k, v in checks.items():
            (passed if v else failed).append(k)

        return {"passed": passed, "failed": failed, "all_passed": len(failed) == 0}

    # ── Signal scoring ────────────────────────────────────────────────────────

    def _signal(self, t: dict, minervini: dict) -> tuple:
        """Return (signal_str, score) where score in [-10, +10]."""
        score = 0

        # RSI
        if t["rsi"] < 30:
            score += 2
        elif t["rsi"] < 45:
            score += 1
        elif t["rsi"] > 75:
            score -= 2
        elif t["rsi"] > 60:
            score -= 1

        # MACD histogram direction
        if t["macd_hist"] > 0 and t["macd"] > t["macd_signal"]:
            score += 2
        elif t["macd_hist"] < 0 and t["macd"] < t["macd_signal"]:
            score -= 2

        # Price vs moving averages
        c = t["close"]
        if c > t["sma200"] > 0:
            score += 1
        elif c < t["sma200"] and t["sma200"] > 0:
            score -= 1
        if c > t["sma50"]:
            score += 1
        else:
            score -= 1
        if c > t["sma20"]:
            score += 1
        else:
            score -= 1

        # Bollinger Band position
        bb_range = t["bb_upper"] - t["bb_lower"]
        if bb_range > 0:
            bb_pct = (c - t["bb_lower"]) / bb_range
            if bb_pct < 0.2:
                score += 1  # near lower band → oversold
            elif bb_pct > 0.8:
                score -= 1  # near upper band → overbought

        # Minervini bonus
        if minervini["all_passed"]:
            score += 2
        else:
            score -= len(minervini["failed"])

        score = max(-10, min(10, score))

        if score >= 5:
            signal = "STRONG BUY"
        elif score >= 2:
            signal = "BUY"
        elif score >= -1:
            signal = "HOLD"
        elif score >= -4:
            signal = "SELL"
        else:
            signal = "STRONG SELL"

        return signal, score

    # ── Entry / Exit / Stop-Loss ──────────────────────────────────────────────

    def _trade_levels(self, t: dict, signal: str) -> dict:
        c = t["close"]
        atr = t["atr"] if t["atr"] > 0 else c * 0.02

        if "BUY" in signal:
            entry = round(c, 2)
            stop_loss = round(c - 1.5 * atr, 2)
            target = round(c + 3.0 * atr, 2)  # 2:1 R/R minimum
        else:
            entry = round(c, 2)
            stop_loss = round(c + 1.5 * atr, 2)
            target = round(c - 3.0 * atr, 2)

        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        rr = round(reward / risk, 2) if risk > 0 else 0

        return {
            "entry": entry,
            "target": target,
            "stop_loss": stop_loss,
            "risk_per_share": round(risk, 2),
            "reward_per_share": round(reward, 2),
            "risk_reward_ratio": rr,
        }

    # ── Holding duration ──────────────────────────────────────────────────────

    def _holding_duration(self, signal: str, t: dict) -> str:
        if "STRONG" in signal:
            return "Short-to-Medium Term (2–8 weeks)"
        if signal == "BUY":
            if t["close"] > t["sma200"] > 0:
                return "Medium-to-Long Term (1–6 months)"
            return "Short Term (1–4 weeks)"
        if signal == "HOLD":
            return "Monitor weekly; re-evaluate on next earnings or macro event"
        return "Exit / Avoid new positions"

    # ── CAPM analysis ─────────────────────────────────────────────────────────

    def _capm(self, df: pd.DataFrame) -> dict:
        nifty = self._nifty_data()
        stock_ret = df["Close"].resample("ME").last().pct_change().dropna()
        nifty_ret = nifty["Close"].resample("ME").last().pct_change().dropna()
        combined = pd.concat([stock_ret, nifty_ret], axis=1).dropna()
        combined.columns = ["stock", "market"]

        if len(combined) < 6:
            return {"beta": None, "alpha": None, "expected_return": None}

        cov = np.cov(combined["stock"], combined["market"])
        beta = round(cov[0, 1] / cov[1, 1], 3)
        market_return = combined["market"].mean() * 12
        rf = self.risk_free_rate
        expected = rf + beta * (market_return - rf)
        actual_annual = combined["stock"].mean() * 12
        alpha = round(actual_annual - expected, 4)

        return {
            "beta": beta,
            "alpha": round(alpha, 4),
            "expected_return": f"{round(expected * 100, 2)} %",
            "actual_annual_return": f"{round(actual_annual * 100, 2)} %",
        }

    # ── Kelly Criterion ───────────────────────────────────────────────────────

    def _kelly(self, df: pd.DataFrame) -> dict:
        ret = df["Close"].pct_change().dropna()
        wins = ret[ret > 0]
        losses = ret[ret < 0]
        if wins.empty or losses.empty:
            return {"kelly_pct": None}
        p = len(wins) / len(ret)
        q = 1 - p
        b = wins.mean() / abs(losses.mean()) if losses.mean() != 0 else 0
        kelly = round((p * b - q) / b * 100, 2) if b > 0 else 0
        kelly = max(0, min(kelly, 25))  # cap at 25 % for safety
        return {"win_prob": f"{round(p*100,1)} %", "win_loss_ratio": round(b, 2), "kelly_pct": f"{kelly} %"}

    # ── Backtest: SMA-20 / 50 crossover ──────────────────────────────────────

    def _backtest(self, df: pd.DataFrame) -> dict:
        close = df["Close"].copy()
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()

        position = 0
        buy_price = 0.0
        trades = []

        for i in range(len(close)):
            if pd.isna(sma20.iloc[i]) or pd.isna(sma50.iloc[i]):
                continue
            if sma20.iloc[i] > sma50.iloc[i] and position == 0:
                position = 1
                buy_price = float(close.iloc[i])
            elif sma20.iloc[i] < sma50.iloc[i] and position == 1:
                position = 0
                sell_price = float(close.iloc[i])
                pct = (sell_price / buy_price - 1) * 100
                trades.append(pct)

        if not trades:
            return {"num_trades": 0, "total_return": "N/A", "win_rate": "N/A", "avg_gain": "N/A", "avg_loss": "N/A", "rr_ratio": "N/A"}

        total_ret = round(np.prod([(p / 100 + 1) for p in trades]) * 100 - 100, 2)
        wins = [p for p in trades if p > 0]
        losses = [p for p in trades if p < 0]
        avg_gain = round(np.mean(wins), 2) if wins else 0
        avg_loss = round(np.mean(losses), 2) if losses else 0
        rr = round(-avg_gain / avg_loss, 2) if avg_loss != 0 else "∞"
        win_rate = round(len(wins) / len(trades) * 100, 1)

        return {
            "num_trades": len(trades),
            "total_return": f"{total_ret} %",
            "win_rate": f"{win_rate} %",
            "avg_gain": f"{avg_gain} %",
            "avg_loss": f"{avg_loss} %",
            "rr_ratio": rr,
        }

    # ── Monte Carlo: 30-day price range ──────────────────────────────────────

    def _monte_carlo(self, df: pd.DataFrame, days: int = 30) -> dict:
        log_ret = np.log(df["Close"] / df["Close"].shift(1)).dropna()
        mu = log_ret.mean()
        sigma = log_ret.std()
        last_price = float(df["Close"].iloc[-1])

        rng = np.random.default_rng(42)
        sims = rng.normal(mu, sigma, (days, self.monte_carlo_sims))
        price_paths = last_price * np.exp(np.cumsum(sims, axis=0))

        final = price_paths[-1, :]
        return {
            "p5": round(float(np.percentile(final, 5)), 2),
            "p50": round(float(np.percentile(final, 50)), 2),
            "p95": round(float(np.percentile(final, 95)), 2),
            "days": days,
        }

    # ── Fundamentals (via yfinance) ───────────────────────────────────────────

    def _fundamentals(self, ticker: str) -> dict:
        info = _yf_info_with_retry(ticker)
        def safe(key, default="N/A"):
            v = info.get(key, default)
            return default if v is None else v

        sector = safe("sector", "Unknown")
        return {
            "sector": sector,
            "industry": safe("industry"),
            "market_cap": safe("marketCap"),
            "pe_ratio": safe("trailingPE"),
            "forward_pe": safe("forwardPE"),
            "eps_ttm": safe("trailingEps"),
            "eps_forward": safe("forwardEps"),
            "peg_ratio": safe("pegRatio"),
            "price_to_book": safe("priceToBook"),
            "debt_to_equity": safe("debtToEquity"),
            "roe": safe("returnOnEquity"),
            "roa": safe("returnOnAssets"),
            "revenue_growth": safe("revenueGrowth"),
            "profit_margin": safe("profitMargins"),
            "dividend_yield": safe("dividendYield"),
            "beta": safe("beta"),
            "52w_high": safe("fiftyTwoWeekHigh"),
            "52w_low": safe("fiftyTwoWeekLow"),
            "analyst_target": safe("targetMeanPrice"),
            "recommendation": safe("recommendationKey", "N/A"),
            "sector_impact": SECTOR_IMPACT.get(sector, SECTOR_IMPACT["Unknown"]),
        }

    # ── Format helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_cap(val) -> str:
        if val == "N/A" or not isinstance(val, (int, float)):
            return "N/A"
        if val >= 1e12:
            return f"₹{val/1e12:.2f}T"
        if val >= 1e9:
            return f"₹{val/1e9:.2f}B"
        if val >= 1e6:
            return f"₹{val/1e6:.2f}M"
        return f"₹{val:,.0f}"

    @staticmethod
    def _fmt_pct(val) -> str:
        if val == "N/A" or not isinstance(val, (int, float)):
            return "N/A"
        return f"{round(val * 100, 2)} %"

    # ── Print report ──────────────────────────────────────────────────────────

    def _print_report(self, symbol: str, result: dict):
        sep = "═" * 72
        thin = "─" * 72
        f = result["fundamentals"]
        t = result["technicals"]
        lv = result["trade_levels"]
        bt = result["backtest"]
        mc = result["monte_carlo"]
        kl = result["kelly"]
        cp = result["capm"]
        mv = result["minervini"]
        sig = result["signal"]
        score = result["score"]

        signal_icon = {"STRONG BUY": "🟢", "BUY": "🟩", "HOLD": "🟡", "SELL": "🟥", "STRONG SELL": "🔴"}.get(sig, "⬜")

        print(f"\n{sep}")
        print(f"  {symbol.replace('.NS','')}  |  {sig} {signal_icon}  (Score: {score}/10)")
        print(f"  {f['industry']}  ·  Sector: {f['sector']}")
        print(sep)

        # ── Recommendation
        print(f"\n  RECOMMENDATION : {sig}")
        print(f"  Analyst Target : {f['analyst_target']}  |  Analyst View: {f['recommendation'].upper()}")
        print(f"  Holding Period : {result['holding_duration']}")

        # ── Sector / Geo-political impact
        print(f"\n{thin}")
        print("  SECTOR & GEOPOLITICAL / GOVERNMENT POLICY IMPACT")
        print(thin)
        print(f"  Sector  : {f['sector']}")
        print(f"  Industry: {f['industry']}")
        print(f"  Impact  : {f['sector_impact']}")

        # ── Technical analysis
        print(f"\n{thin}")
        print("  TECHNICAL ANALYSIS")
        print(thin)
        print(f"  Current Price : ₹{t['close']}")
        print(f"  RSI (14)      : {t['rsi']}  {'← Oversold' if t['rsi'] < 30 else ('← Overbought' if t['rsi'] > 70 else '')}")
        print(f"  MACD          : {t['macd']:.4f}  |  Signal: {t['macd_signal']:.4f}  |  Hist: {t['macd_hist']:.4f}")
        print(f"  SMA 20 / 50   : {t['sma20']} / {t['sma50']}")
        print(f"  SMA 150 / 200 : {t['sma150']} / {t['sma200']}")
        print(f"  EMA 20        : {t['ema20']}")
        print(f"  Bollinger     : Upper {t['bb_upper']}  |  Mid {t['bb_mid']}  |  Lower {t['bb_lower']}")
        print(f"  ATR (14)      : {t['atr']}")
        print(f"  52W High/Low  : {t['52w_high']} / {t['52w_low']}")
        print(f"  Avg Volume 20D: {t['vol_avg20']:,}")

        # Minervini conditions
        print(f"\n  Minervini Trend Template:")
        for c in mv["passed"]:
            print(f"    ✔  {c}")
        for c in mv["failed"]:
            print(f"    ✘  {c}")

        # ── Fundamentals
        print(f"\n{thin}")
        print("  FUNDAMENTAL ANALYSIS")
        print(thin)
        print(f"  Market Cap      : {self._fmt_cap(f['market_cap'])}")
        print(f"  P/E (TTM)       : {f['pe_ratio']}  |  Forward P/E: {f['forward_pe']}")
        print(f"  EPS (TTM)       : {f['eps_ttm']}  |  Forward EPS: {f['eps_forward']}")
        print(f"  PEG Ratio       : {f['peg_ratio']}")
        print(f"  Price/Book      : {f['price_to_book']}")
        print(f"  Debt/Equity     : {f['debt_to_equity']}")
        print(f"  ROE             : {self._fmt_pct(f['roe'])}")
        print(f"  ROA             : {self._fmt_pct(f['roa'])}")
        print(f"  Revenue Growth  : {self._fmt_pct(f['revenue_growth'])}")
        print(f"  Profit Margin   : {self._fmt_pct(f['profit_margin'])}")
        print(f"  Dividend Yield  : {self._fmt_pct(f['dividend_yield'])}")
        print(f"  Beta (yfinance) : {f['beta']}")

        # ── CAPM
        print(f"\n{thin}")
        print("  CAPM ANALYSIS  (vs NIFTY 50)")
        print(thin)
        if cp["beta"] is not None:
            print(f"  Beta            : {cp['beta']}")
            print(f"  Alpha           : {cp['alpha']}")
            print(f"  Expected Return : {cp['expected_return']}")
            print(f"  Actual Return   : {cp['actual_annual_return']}")
        else:
            print("  Insufficient data for CAPM.")

        # ── Kelly Criterion / Position sizing
        print(f"\n{thin}")
        print("  POSITION SIZING  (Kelly Criterion)")
        print(thin)
        if kl["kelly_pct"] is not None:
            print(f"  Win Probability : {kl['win_prob']}")
            print(f"  Win / Loss Ratio: {kl['win_loss_ratio']}")
            print(f"  Kelly %         : {kl['kelly_pct']}  ← max % of portfolio to allocate")
        else:
            print("  Insufficient data for Kelly Criterion.")

        # ── Trade levels
        print(f"\n{thin}")
        print("  ENTRY · EXIT · STOP-LOSS")
        print(thin)
        print(f"  Entry (current) : ₹{lv['entry']}")
        print(f"  Target (exit)   : ₹{lv['target']}")
        print(f"  Stop-Loss       : ₹{lv['stop_loss']}")
        print(f"  Risk per share  : ₹{lv['risk_per_share']}")
        print(f"  Reward/share    : ₹{lv['reward_per_share']}")
        print(f"  Risk/Reward     : 1 : {lv['risk_reward_ratio']}")

        # ── Backtest
        print(f"\n{thin}")
        print("  BACKTEST  (SMA-20 / SMA-50 Crossover  –  last {self.lookback_years} years)")
        print(thin)
        print(f"  Total Return    : {bt['total_return']}")
        print(f"  # Trades        : {bt['num_trades']}")
        print(f"  Win Rate        : {bt['win_rate']}")
        print(f"  Avg Gain        : {bt['avg_gain']}")
        print(f"  Avg Loss        : {bt['avg_loss']}")
        print(f"  R/R Ratio       : {bt['rr_ratio']}")

        # ── Monte Carlo
        print(f"\n{thin}")
        print(f"  MONTE CARLO  ({mc['days']}-day Price Range  |  {self.monte_carlo_sims} simulations)")
        print(thin)
        print(f"  Bearish (5th pct) : ₹{mc['p5']}")
        print(f"  Base    (median)  : ₹{mc['p50']}")
        print(f"  Bullish (95th pct): ₹{mc['p95']}")

        print(f"\n{sep}\n")

    # ── Summary table ─────────────────────────────────────────────────────────

    def _print_summary(self, all_results: list):
        print("\n" + "═" * 72)
        print("  SUMMARY TABLE  –  All NSE Stocks Analysed")
        print("═" * 72)
        header = f"{'Symbol':<14} {'Signal':<13} {'Score':>5} {'Price':>8} {'RSI':>6} {'Target':>8} {'SL':>8} {'R:R':>5}"
        print(header)
        print("─" * 72)
        for r in sorted(all_results, key=lambda x: x["score"], reverse=True):
            sym = r["symbol"].replace(".NS", "")
            lv = r["trade_levels"]
            t = r["technicals"]
            print(
                f"{sym:<14} {r['signal']:<13} {r['score']:>5} "
                f"{t['close']:>8.2f} {t['rsi']:>6.1f} "
                f"{lv['target']:>8.2f} {lv['stop_loss']:>8.2f} {str(lv['risk_reward_ratio']):>5}"
            )
        print("═" * 72 + "\n")

    # ── Main analysis loop ────────────────────────────────────────────────────

    def analyze(self, verbose: bool = True) -> pd.DataFrame:
        """
        Run the full analysis on all tickers in Nse_tickers.csv.

        Parameters
        ----------
        verbose : bool
            Print detailed per-stock report (default True).

        Returns
        -------
        pd.DataFrame  Summary DataFrame.
        """
        all_results = []

        for ticker in self.tickers:
            symbol = ticker
            print(f"  Analysing {symbol} ...", end="\r")
            try:
                df = self._download(ticker)
                t = self._technicals(df)
                mv = self._minervini_check(t)
                sig, score = self._signal(t, mv)
                lv = self._trade_levels(t, sig)
                dur = self._holding_duration(sig, t)
                bt = self._backtest(df)
                mc = self._monte_carlo(df)
                kl = self._kelly(df)
                cp = self._capm(df)
                fu = self._fundamentals(ticker)

                result = {
                    "symbol": symbol,
                    "signal": sig,
                    "score": score,
                    "technicals": t,
                    "minervini": mv,
                    "trade_levels": lv,
                    "holding_duration": dur,
                    "backtest": bt,
                    "monte_carlo": mc,
                    "kelly": kl,
                    "capm": cp,
                    "fundamentals": fu,
                }

                all_results.append(result)
                if verbose:
                    self._print_report(symbol, result)

            except Exception as e:
                print(f"  \u26a0  Skipped {symbol}: {e}")
            time.sleep(2.5)  # rate-limit: avoid Yahoo Finance blocking

        # Summary table
        if all_results:
            self._print_summary(all_results)

        # Return as DataFrame
        rows = []
        for r in all_results:
            t = r["technicals"]
            lv = r["trade_levels"]
            f = r["fundamentals"]
            bt = r["backtest"]
            mc = r["monte_carlo"]
            rows.append({
                "Symbol": r["symbol"].replace(".NS", ""),
                "Signal": r["signal"],
                "Score": r["score"],
                "Price": t["close"],
                "RSI": t["rsi"],
                "MACD_Hist": t["macd_hist"],
                "SMA20": t["sma20"],
                "SMA50": t["sma50"],
                "Entry": lv["entry"],
                "Target": lv["target"],
                "StopLoss": lv["stop_loss"],
                "RiskReward": lv["risk_reward_ratio"],
                "Sector": f["sector"],
                "MarketCap": f["market_cap"],
                "PE_TTM": f["pe_ratio"],
                "EPS_TTM": f["eps_ttm"],
                "ROE": f["roe"],
                "DebtEquity": f["debt_to_equity"],
                "Backtest_Return": bt["total_return"],
                "Backtest_WinRate": bt["win_rate"],
                "MC_Bear": mc["p5"],
                "MC_Base": mc["p50"],
                "MC_Bull": mc["p95"],
                "HoldingDuration": r["holding_duration"],
            })

        return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "Nse_tickers.csv")
    analyzer = NSEStockAnalyzer(
        csv_path=csv_path,
        lookback_years=2,
        risk_free_rate=0.065,  # 6.5% India 10-yr Gsec yield
        monte_carlo_sims=500,
    )
    summary_df = analyzer.analyze(verbose=True)

    # Save summary CSV
    out = os.path.join(os.path.dirname(__file__), "nse_analysis_results.csv")
    summary_df.to_csv(out, index=False)
    print(f"Results saved to: {out}")
