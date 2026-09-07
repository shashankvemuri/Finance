from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import finite


@dataclass(frozen=True)
class Valuation:
    enterprise_value: float
    equity_value: float
    value_per_share: float
    present_values: pd.Series
    terminal_present_value: float


def discounted_cash_flow(
    cash_flows: Sequence[float],
    discount_rate: float,
    terminal_growth: float = 0.02,
    *,
    cash: float = 0,
    debt: float = 0,
    shares: float = 1,
) -> Valuation:
    """Year-end unlevered cash flows; terminal value at final year; all amounts share a currency."""
    flows = np.asarray(cash_flows, dtype=float)
    if flows.ndim != 1 or not len(flows) or not np.isfinite(flows).all():
        raise ValueError("provide finite annual cash flows")
    for name, value in [("discount_rate", discount_rate), ("terminal_growth", terminal_growth)]:
        finite(value, name)
    if discount_rate <= terminal_growth or terminal_growth <= -1:
        raise ValueError("require discount_rate > terminal_growth > -1")
    if flows[-1] < 0:
        raise ValueError("perpetuity requires nonnegative terminal cash flow")
    for name, value in [("cash", cash), ("debt", debt)]:
        finite(value, name, minimum=0)
    finite(shares, "shares", minimum=np.finfo(float).tiny)
    years = np.arange(1, len(flows) + 1)
    present = flows / (1 + discount_rate) ** years
    terminal = (
        flows[-1]
        * (1 + terminal_growth)
        / (discount_rate - terminal_growth)
        / (1 + discount_rate) ** len(flows)
    )
    enterprise = float(present.sum() + terminal)
    equity = enterprise + cash - debt
    return Valuation(
        enterprise,
        equity,
        equity / shares,
        pd.Series(present, index=years, name="present_value"),
        float(terminal),
    )


def scenario_valuation(
    cash_flows: dict[str, Sequence[float]],
    discount_rates: Sequence[float],
    terminal_growth: float = 0.02,
) -> pd.DataFrame:
    """Sensitivity table of enterprise values (or dividend values for per-share payouts)."""
    if not cash_flows or not len(discount_rates):
        raise ValueError("provide scenarios and discount rates")
    return pd.DataFrame(
        {
            name: [
                discounted_cash_flow(flows, rate, terminal_growth).enterprise_value
                for rate in discount_rates
            ]
            for name, flows in cash_flows.items()
        },
        index=pd.Index(discount_rates, name="discount_rate"),
    )


def fundamental_ratios(
    *,
    price: float,
    earnings_per_share: float,
    book_value_per_share: float,
    annual_dividend: float = 0,
) -> pd.Series:
    finite(price, "price", minimum=np.finfo(float).tiny)
    finite(earnings_per_share, "earnings_per_share")
    finite(book_value_per_share, "book_value_per_share")
    finite(annual_dividend, "annual_dividend", minimum=0)
    return pd.Series(
        {
            "pe": price / earnings_per_share if earnings_per_share > 0 else np.nan,
            "price_to_book": price / book_value_per_share if book_value_per_share > 0 else np.nan,
            "dividend_yield": annual_dividend / price,
        }
    )
