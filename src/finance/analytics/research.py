"""Calendar studies and explicit company/index valuation assumptions."""

from collections.abc import Sequence

import numpy as np
import pandas as pd

from finance._validation import series
from finance.analytics.valuation import discounted_cash_flow


def seasonal_entries(
    close: pd.Series, month: int, day: int, holding_months: int = 1
) -> pd.DataFrame:
    """First observed close on/after calendar dates; completed holds only. Descriptive, overlapping samples."""
    close = series(close, positive=True, missing=False)
    if not isinstance(close.index, pd.DatetimeIndex) or not close.index.is_monotonic_increasing:
        raise ValueError("require chronologically indexed prices")
    if not 1 <= holding_months <= 36:
        raise ValueError("holding_months must be 1–36")
    pd.Timestamp(2000, month, day)
    rows = []
    for year in close.index.year.unique():
        try:
            scheduled = pd.Timestamp(year, month, day, tz=close.index.tz)
        except ValueError:
            continue  # February 29 is absent in non-leap years.
        if scheduled < close.index[0]:
            continue
        entry = close.index.searchsorted(scheduled)
        if entry == len(close):
            continue
        due = close.index[entry] + pd.DateOffset(months=holding_months)
        exit = close.index.searchsorted(due)
        if exit == len(close):
            continue
        rows.append(
            {
                "year": year,
                "entry": close.index[entry],
                "exit": close.index[exit],
                "entry_price": close.iloc[entry],
                "exit_price": close.iloc[exit],
                "return": close.iloc[exit] / close.iloc[entry] - 1,
            }
        )
    return pd.DataFrame(
        rows, columns=["year", "entry", "exit", "entry_price", "exit_price", "return"]
    )


def seasonal_summary(
    prices: pd.DataFrame, month: int, day: int, holding_months: int = 1
) -> pd.DataFrame:
    rows = []
    for ticker in prices:
        study = seasonal_entries(prices[ticker], month, day, holding_months)
        rows.append(
            {
                "ticker": ticker,
                "observations": len(study),
                "mean_return": study["return"].mean(),
                "median_return": study["return"].median(),
                "win_rate": (study["return"] > 0).mean() if len(study) else np.nan,
            }
        )
    return pd.DataFrame(rows).set_index("ticker")


def company_cash_flows(income: pd.DataFrame, cashflow: pd.DataFrame) -> pd.DataFrame:
    """FCFF = operating income × (1-tax) + D&A + signed capex + cash change in working capital.

    Uses reported cash-flow signs: capex is negative, a working-capital cash release positive.
    Stock compensation is not added back. This operating-company approximation excludes banks.
    """
    required = ["Operating Income", "Tax Provision", "Pretax Income"]
    cash_columns = [
        "Depreciation And Amortization",
        "Capital Expenditure",
        "Change In Working Capital",
    ]
    if not set(required) <= set(income) or not set(cash_columns) <= set(cashflow):
        raise ValueError(
            "statements require operating income, tax, pretax income, D&A, capex and working capital"
        )
    left_currency, right_currency = income.attrs.get("currency"), cashflow.attrs.get("currency")
    if left_currency and right_currency and left_currency != right_currency:
        raise ValueError("statement currencies differ")
    data = income[required].join(cashflow[cash_columns], how="inner").sort_index()
    if data.empty or data.iloc[-1].isna().any():
        raise ValueError(
            "latest common statement period is incomplete; supply complete inputs explicitly"
        )
    data = data.dropna()
    if not np.isfinite(data).all().all() or (data["Pretax Income"] <= 0).any():
        raise ValueError("require complete periods with positive pretax income")
    rate = data["Tax Provision"] / data["Pretax Income"]
    if (
        not rate.between(0, 1).all()
        or (data["Capital Expenditure"] > 0).any()
        or (data["Depreciation And Amortization"] < 0).any()
    ):
        raise ValueError("invalid tax rate, depreciation or capex sign")
    result = pd.DataFrame(
        {
            "tax_rate": rate,
            "after_tax_operating_income": data["Operating Income"] * (1 - rate),
            "depreciation": data["Depreciation And Amortization"],
            "capex": data["Capital Expenditure"],
            "working_capital_cash_change": data["Change In Working Capital"],
        }
    )
    result["fcff"] = result.drop(columns="tax_rate").sum(axis=1)
    result.attrs.update(currency=left_currency, frequency=income.attrs.get("frequency"))
    return result


def company_scenarios(
    base_fcff: float,
    growth_paths: dict[str, Sequence[float]],
    discount_rate: float,
    *,
    terminal_growth: float = 0.025,
    cash: float = 0,
    debt: float = 0,
    shares: float = 1,
    price: float | None = None,
) -> pd.DataFrame:
    if not np.isfinite(base_fcff) or base_fcff <= 0 or not growth_paths:
        raise ValueError("positive base FCFF and growth scenarios required")
    if price is not None and (not np.isfinite(price) or price <= 0):
        raise ValueError("price must be positive")
    rows = []
    for name, growth in growth_paths.items():
        growth = np.asarray(growth, dtype=float)
        if (
            growth.ndim != 1
            or not len(growth)
            or not np.isfinite(growth).all()
            or (growth <= -1).any()
        ):
            raise ValueError("growth paths must be nonempty, finite and above -1")
        value = discounted_cash_flow(
            base_fcff * np.cumprod(1 + growth),
            discount_rate,
            terminal_growth,
            cash=cash,
            debt=debt,
            shares=shares,
        )
        rows.append(
            {
                "scenario": name,
                "enterprise_value": value.enterprise_value,
                "equity_value": value.equity_value,
                "value_per_share": value.value_per_share,
                "upside": value.value_per_share / price - 1 if price else np.nan,
            }
        )
    return pd.DataFrame(rows).set_index("scenario")


def index_scenarios(
    earnings: float,
    growth_paths: dict[str, Sequence[float]],
    *,
    payout: float,
    discount_rate: float,
    terminal_growth: float = 0.025,
) -> pd.DataFrame:
    """Dividend-discount scenarios from index EPS and an explicit payout fraction."""
    if not np.isfinite(earnings) or earnings <= 0 or not 0 < payout <= 1:
        raise ValueError("positive index EPS and payout in (0,1] required")
    result = company_scenarios(
        earnings * payout, growth_paths, discount_rate, terminal_growth=terminal_growth
    )
    return result[["value_per_share"]].rename(columns={"value_per_share": "index_value"})


def statement_ratios(income: pd.DataFrame, balance: pd.DataFrame) -> pd.DataFrame:
    """Period-aligned margins and balance ratios. ROE uses average beginning/end equity."""
    required_income = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
    required_balance = [
        "Total Assets",
        "Stockholders Equity",
        "Total Debt",
        "Current Assets",
        "Current Liabilities",
    ]
    if not set(required_income) <= set(income) or not set(required_balance) <= set(balance):
        raise ValueError("missing required income/balance statement fields")
    left, right = income.attrs.get("currency"), balance.attrs.get("currency")
    if left and right and left != right:
        raise ValueError("statement currencies differ")
    data = income[required_income].join(balance[required_balance], how="inner").sort_index()
    if data.empty:
        raise ValueError("no common reporting periods")
    revenue = data["Total Revenue"].where(data["Total Revenue"] > 0)
    equity = data["Stockholders Equity"].where(data["Stockholders Equity"] > 0)
    average_equity = (equity + equity.shift()) / 2
    return pd.DataFrame(
        {
            "gross_margin": data["Gross Profit"] / revenue,
            "operating_margin": data["Operating Income"] / revenue,
            "net_margin": data["Net Income"] / revenue,
            "roe": data["Net Income"] / average_equity,
            "debt_equity": data["Total Debt"] / equity,
            "current_ratio": data["Current Assets"]
            / data["Current Liabilities"].where(data["Current Liabilities"] > 0),
            "revenue_growth": revenue.pct_change(fill_method=None),
        }
    )
