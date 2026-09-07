import numpy as np
import pandas as pd

from finance._validation import frame, series, window_size
from finance.data import normalize_ohlcv
from finance.indicators import rsi, sma


def relative_strength(
    prices: pd.DataFrame, benchmark: pd.Series, window: int = 252
) -> pd.DataFrame:
    """Gross-return ratio and percentile rank within the supplied universe."""
    prices, benchmark = (
        frame(prices, positive=True),
        series(benchmark, positive=True, missing=False),
    )
    window_size(window)
    if not prices.index.equals(benchmark.index) or len(prices) <= window:
        raise ValueError("aligned prices need at least window+1 observations")
    asset_return = prices.iloc[-1] / prices.iloc[-window - 1] - 1
    market_gross = benchmark.iloc[-1] / benchmark.iloc[-window - 1]
    relative = (1 + asset_return) / market_gross
    return pd.DataFrame(
        {
            "return": asset_return,
            "relative_strength": relative,
            "rank": relative.rank(pct=True) * 100,
        }
    ).sort_values("rank", ascending=False)


def ibd_relative_strength(prices: pd.DataFrame) -> pd.DataFrame:
    """IBD-inspired 40/20/20/20 weighting of trailing 3/6/9/12-month returns; not proprietary IBD ratings."""
    prices = frame(prices, positive=True)
    if len(prices) < 253:
        raise ValueError("at least 253 observations required")
    score = sum(
        weight * (prices.iloc[-1] / prices.iloc[-days - 1] - 1)
        for weight, days in zip((0.4, 0.2, 0.2, 0.2), (63, 126, 189, 252), strict=True)
    )
    return pd.DataFrame({"score": score, "rank": score.rank(pct=True) * 100}).sort_values(
        "rank", ascending=False
    )


def minervini(
    prices: dict[str, pd.DataFrame], benchmark: pd.Series, *, minimum_rank: float = 70
) -> pd.DataFrame:
    """Trend-template diagnostics for every ticker; select passed rows explicitly."""
    if not 0 <= minimum_rank <= 100 or not prices:
        raise ValueError("provide prices and a rank threshold in [0,100]")
    normalized = {ticker: normalize_ohlcv(data) for ticker, data in prices.items()}
    closes = pd.DataFrame({ticker: data.close for ticker, data in normalized.items()})
    if closes.isna().any().any():
        raise ValueError("align complete histories before screening")
    ranks = relative_strength(closes, benchmark)
    rows = []
    for ticker, data in normalized.items():
        close = data.close
        ma50, ma150, ma200 = sma(close, 50), sma(close, 150), sma(close, 200)
        low, high = data.low.iloc[-252:].min(), data.high.iloc[-252:].max()
        last = close.iloc[-1]
        checks = {
            "above_averages": last > ma50.iloc[-1] > ma150.iloc[-1] > ma200.iloc[-1],
            "rising_200": ma200.iloc[-1] > ma200.iloc[-21],
            "above_low": last >= 1.3 * low,
            "near_high": last >= 0.75 * high,
            "strong_rank": ranks.loc[ticker, "rank"] >= minimum_rank,
        }
        rows.append(
            {
                "ticker": ticker,
                "close": last,
                "sma50": ma50.iloc[-1],
                "sma150": ma150.iloc[-1],
                "sma200": ma200.iloc[-1],
                "low_52w": low,
                "high_52w": high,
                "rs_rank": ranks.loc[ticker, "rank"],
                **checks,
                "passed": all(checks.values()),
            }
        )
    return pd.DataFrame(rows).set_index("ticker").sort_values("rs_rank", ascending=False)


def rsi_screen(
    prices: pd.DataFrame, window: int = 14, lower: float = 30, upper: float = 70
) -> pd.DataFrame:
    prices = frame(prices, positive=True)
    if not 0 <= lower < upper <= 100 or len(prices) <= window:
        raise ValueError("require ordered RSI thresholds and enough history")
    values = prices.apply(lambda close: rsi(close, window).iloc[-1])
    return pd.DataFrame({"rsi": values, "oversold": values <= lower, "overbought": values >= upper})


def fundamental_screen(
    companies: pd.DataFrame,
    *,
    minimum_roe: float = 0.1,
    minimum_growth: float = 0.1,
    maximum_pe: float = 40,
) -> pd.DataFrame:
    """Concrete quality/growth/value screen on fractional ratios; missing fields fail the screen."""
    required = ["roe", "revenue_growth", "earnings_growth", "pe"]
    if not set(required) <= set(companies):
        raise ValueError(f"required columns: {required}")
    values = companies[required].apply(pd.to_numeric, errors="raise")
    valid = np.isfinite(values).all(axis=1)
    passed = (
        valid
        & (values.roe >= minimum_roe)
        & (values.revenue_growth >= minimum_growth)
        & (values.earnings_growth >= minimum_growth)
        & values.pe.between(0, maximum_pe, inclusive="right")
    )
    return companies.copy().assign(passed=passed)


def dividend_screen(companies: pd.DataFrame, minimum_yield: float = 0.02) -> pd.DataFrame:
    if not 0 <= minimum_yield <= 1 or "dividend_yield" not in companies:
        raise ValueError("provide fractional dividend_yield and threshold in [0,1]")
    yields = pd.to_numeric(companies.dividend_yield, errors="raise")
    return companies.assign(
        passed=np.isfinite(yields) & yields.between(minimum_yield, 1)
    ).sort_values("dividend_yield", ascending=False)


def technical_screen(close: pd.Series) -> pd.Series:
    """Transparent MA/RSI/MACD votes; no claim to reproduce a vendor recommendation."""
    from finance.indicators import macd

    close = series(close, positive=True, missing=False)
    if len(close) < 200:
        raise ValueError("at least 200 bars required")
    return pd.Series(
        {
            "above_sma50": close.iloc[-1] > sma(close, 50).iloc[-1],
            "above_sma200": close.iloc[-1] > sma(close, 200).iloc[-1],
            "positive_macd": macd(close).histogram.iloc[-1] > 0,
            "rsi": rsi(close).iloc[-1],
        }
    )
