"""FIFO matching of fills; open quantities remain unrealized."""

from collections import defaultdict, deque

import numpy as np
import pandas as pd


def completed_trades(fills: pd.DataFrame) -> pd.DataFrame:
    """One row per matched lot portion; commissions allocated by quantity, excludes borrow costs."""
    required = ["date", "asset", "quantity", "price", "commission"]
    if not set(required) <= set(fills):
        raise ValueError(f"required fill columns: {required}")
    values = fills[["quantity", "price", "commission"]]
    if (
        not np.isfinite(values).all().all()
        or (fills.price <= 0).any()
        or (fills.commission < 0).any()
    ):
        raise ValueError("finite quantities, positive prices and nonnegative fees required")
    if not pd.Index(fills.date).is_monotonic_increasing:
        raise ValueError("fills must be chronological, preserving within-bar execution order")
    lots, rows = defaultdict(deque), []
    for fill in fills.itertuples():
        remaining = float(fill.quantity)
        if remaining == 0:
            if fill.commission != 0:
                raise ValueError("zero-quantity fills cannot carry commissions")
            continue
        fee_per_share = fill.commission / abs(remaining)
        book = lots[fill.asset]
        while book and np.sign(book[0]["quantity"]) != np.sign(remaining):
            lot = book[0]
            matched = min(abs(lot["quantity"]), abs(remaining))
            side = np.sign(lot["quantity"])
            gross = side * matched * (fill.price - lot["price"])
            fees = matched * (lot["fee"] + fee_per_share)
            rows.append(
                {
                    "asset": fill.asset,
                    "entry_date": lot["date"],
                    "exit_date": fill.date,
                    "side": "long" if side > 0 else "short",
                    "quantity": matched,
                    "entry_price": lot["price"],
                    "exit_price": fill.price,
                    "gross_pnl": gross,
                    "commission": fees,
                    "net_pnl": gross - fees,
                    "return": (gross - fees) / (matched * lot["price"]),
                    "duration": pd.Timestamp(fill.date) - pd.Timestamp(lot["date"]),
                }
            )
            lot["quantity"] -= side * matched
            remaining += side * matched
            if abs(lot["quantity"]) < 1e-10:
                book.popleft()
            if abs(remaining) < 1e-10:
                remaining = 0
                break
        if remaining:
            book.append(
                {
                    "quantity": remaining,
                    "price": fill.price,
                    "date": fill.date,
                    "fee": fee_per_share,
                }
            )
    return pd.DataFrame(
        rows,
        columns=[
            "asset",
            "entry_date",
            "exit_date",
            "side",
            "quantity",
            "entry_price",
            "exit_price",
            "gross_pnl",
            "commission",
            "net_pnl",
            "return",
            "duration",
        ],
    )


def trade_statistics(trades: pd.DataFrame) -> pd.Series:
    if not {"net_pnl", "return", "duration"} <= set(trades):
        raise ValueError("provide completed_trades output")
    wins, losses = (
        trades.loc[trades.net_pnl > 0, "net_pnl"],
        trades.loc[trades.net_pnl < 0, "net_pnl"],
    )
    return pd.Series(
        {
            "matched_lots": len(trades),
            "win_rate": (trades.net_pnl > 0).mean(),
            "average_win": wins.mean(),
            "average_loss": losses.mean(),
            "profit_factor": wins.sum() / -losses.sum() if len(losses) else np.nan,
            "net_pnl": trades.net_pnl.sum(),
            "mean_return": trades["return"].mean(),
            "mean_holding_days": trades.duration.dt.total_seconds().mean() / 86400
            if len(trades)
            else np.nan,
        }
    )
