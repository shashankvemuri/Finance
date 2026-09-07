import numpy as np
import pandas as pd

from finance._validation import finite, series, window_size


def returns(prices: pd.Series | pd.DataFrame, *, log: bool = False) -> pd.Series | pd.DataFrame:
    """Fractional simple or log returns; missing observations are never filled."""
    if isinstance(prices, pd.DataFrame):
        if prices.empty or not prices.columns.is_unique:
            raise ValueError("expected nonempty prices with unique columns")
        return prices.apply(lambda col: returns(col, log=log))
    prices = series(prices, positive=True)
    return np.log(prices).diff() if log else prices.pct_change(fill_method=None)


def cumulative_returns(values: pd.Series) -> pd.Series:
    values = series(values, missing=False)
    if (values < -1).any():
        raise ValueError("simple returns cannot be below -100%")
    return (1 + values).cumprod() - 1


def drawdown(equity: pd.Series, *, initial: float | None = None) -> pd.Series:
    equity = series(equity, positive=True, missing=False)
    peak = equity.cummax()
    if initial is not None:
        finite(initial, "initial", minimum=np.finfo(float).tiny)
        peak = peak.clip(lower=initial)
    return equity / peak - 1


def performance(values: pd.Series, periods: int = 252, risk_free: float = 0) -> pd.Series:
    """Returns-based metrics; annual risk-free rate, sample volatility, initial wealth included."""
    values = series(values, missing=False)
    window_size(periods)
    if (values <= -1).any():
        raise ValueError("performance requires returns above -100%")
    finite(risk_free, "risk_free")
    if risk_free <= -1:
        raise ValueError("risk_free must exceed -1")
    wealth = (1 + values).cumprod()
    total = wealth.iloc[-1] - 1
    cagr = wealth.iloc[-1] ** (periods / len(values)) - 1
    volatility = values.std(ddof=1) * np.sqrt(periods)
    excess = values - ((1 + risk_free) ** (1 / periods) - 1)
    sharpe = excess.mean() * periods / volatility if volatility > 0 else np.nan
    downside = np.sqrt(np.mean(np.minimum(excess, 0) ** 2)) * np.sqrt(periods)
    maximum_drawdown = drawdown(wealth, initial=1).min()
    return pd.Series(
        {
            "total_return": total,
            "cagr": cagr,
            "volatility": volatility,
            "sharpe": sharpe,
            "sortino": excess.mean() * periods / downside if downside > 0 else np.nan,
            "max_drawdown": maximum_drawdown,
            "calmar": cagr / -maximum_drawdown if maximum_drawdown < 0 else np.nan,
        }
    )


def period_returns(prices: pd.Series, frequency: str = "ME") -> pd.Series:
    prices = series(prices, positive=True, missing=False)
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("period returns require a DatetimeIndex")
    return returns(prices.resample(frequency).last()).dropna()


def seasonality(prices: pd.Series) -> pd.DataFrame:
    """Descriptive calendar-month returns; incomplete endpoint months are excluded."""
    prices = series(prices, positive=True, missing=False)
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("seasonality requires dates")
    monthly = period_returns(prices)
    last_complete = prices.index[-1].to_period("M")
    if prices.index[-1].date() < (prices.index[-1] + pd.offsets.BMonthEnd(0)).date():
        monthly = monthly[monthly.index.to_period("M") < last_complete]
    groups = monthly.groupby(monthly.index.month)
    return groups.agg(["count", "mean", "median", "std"]).assign(
        win_rate=groups.apply(lambda x: (x > 0).mean())
    )


def pnl(prices: pd.Series, shares: float, purchase_price: float, fees: float = 0) -> pd.Series:
    prices = series(prices, positive=True, missing=False)
    finite(shares, "shares")
    finite(purchase_price, "purchase_price", minimum=np.finfo(float).tiny)
    finite(fees, "fees", minimum=0)
    return shares * (prices - purchase_price) - fees


def distribution(values: pd.Series) -> pd.Series:
    values = series(values, missing=False)
    return pd.Series(
        {
            "count": len(values),
            "mean": values.mean(),
            "std": values.std(),
            "skew": values.skew(),
            "excess_kurtosis": values.kurt(),
            "q05": values.quantile(0.05),
            "median": values.median(),
            "q95": values.quantile(0.95),
        }
    )
