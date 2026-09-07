from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import finite, frame, window_size
from finance.analytics import performance


@dataclass(frozen=True)
class BacktestResult:
    equity: pd.Series
    cash: pd.Series
    holdings: pd.DataFrame
    trades: pd.DataFrame
    returns: pd.Series
    benchmark: pd.Series
    metrics: pd.Series


def backtest(
    open_prices: pd.Series | pd.DataFrame,
    close_prices: pd.Series | pd.DataFrame,
    targets: pd.Series | pd.DataFrame,
    *,
    initial_cash: float = 10000,
    commission: float = 0.001,
    slippage: float = 0,
    borrow_rate: float = 0,
    periods: int = 252,
    rebalance: bool = False,
    liquidate: bool = False,
) -> BacktestResult:
    """Close signals execute next open. Gross target <=1; fractional shares, no cash interest.

    Rebalance on target changes (or every bar with rebalance=True). Trade rows are fills,
    including partial adjustments. Adjusted OHLC must share a basis. Short borrow is charged
    on each held bar's opening notional. No intrabar stops, margin loans, or volume limits.
    """

    def as_frame(data):
        return data.to_frame("asset") if isinstance(data, pd.Series) else data

    opens, closes, targets = (
        frame(as_frame(open_prices), positive=True),
        frame(as_frame(close_prices), positive=True),
        frame(as_frame(targets)),
    )
    if not opens.index.equals(closes.index) or not opens.index.equals(targets.index):
        raise ValueError("open, close and target timestamps must match exactly")
    if not opens.columns.equals(closes.columns) or not opens.columns.equals(targets.columns):
        raise ValueError("open, close and target asset columns must match exactly")
    if len(opens) < 2 or (targets.abs().sum(axis=1) > 1 + 1e-12).any():
        raise ValueError("require at least two bars and gross targets <= 1")
    finite(initial_cash, "initial_cash", minimum=np.finfo(float).tiny)
    for name, cost in [
        ("commission", commission),
        ("slippage", slippage),
        ("borrow_rate", borrow_rate),
    ]:
        finite(cost, name, minimum=0)
        if cost >= 1:
            raise ValueError(f"{name} must be below 1")
    window_size(periods)
    cash, shares = float(initial_cash), np.zeros(opens.shape[1])
    cash_rows, equity_rows, holding_rows, fills = [], [], [], []
    prior_target = np.zeros(opens.shape[1])
    fees_total = borrow_total = 0.0
    open_values, close_values = opens.to_numpy(), closes.to_numpy()
    # At bar t only the signal from t-1 is available.
    delayed = targets.shift(1, fill_value=0).to_numpy()

    def execute(quantity, price, timestamp, signal_time, phase):
        nonlocal cash, shares, fees_total
        for j, delta in enumerate(quantity):
            if abs(delta) < 1e-10:
                continue
            fill_price = price[j] * (1 + np.sign(delta) * slippage)
            fee = abs(delta) * fill_price * commission
            cash -= delta * fill_price + fee
            shares[j] += delta
            fees_total += fee
            fills.append(
                {
                    "date": timestamp,
                    "signal_date": signal_time,
                    "asset": opens.columns[j],
                    "quantity": delta,
                    "price": fill_price,
                    "commission": fee,
                    "phase": phase,
                }
            )

    for i, timestamp in enumerate(opens.index):
        price, close, target = open_values[i], close_values[i], delayed[i]
        equity_at_open = cash + shares @ price
        if equity_at_open <= 0:
            raise ValueError(f"account insolvent at {timestamp}; short losses exceeded equity")
        if rebalance or not np.array_equal(target, prior_target):
            # Solve for post-cost equity so a fully invested long never overspends cash.
            def residual(equity, target=target, price=price, equity_at_open=equity_at_open):
                quantity = target * equity / price - shares
                fill = price * (1 + np.sign(quantity) * slippage)
                costs = np.sum(quantity * (fill - price) + np.abs(quantity) * fill * commission)
                return equity + costs - equity_at_open

            if residual(0) > 0:
                raise ValueError(f"costs exceed equity at {timestamp}")
            lower, upper = 0.0, equity_at_open
            for _ in range(60):
                middle = (lower + upper) / 2
                if residual(middle) > 0:
                    upper = middle
                else:
                    lower = middle
            desired = target * ((lower + upper) / 2) / price
            execute(desired - shares, price, timestamp, opens.index[i - 1] if i else pd.NaT, "open")
        prior_target = target.copy()
        borrow = np.maximum(-shares, 0) @ price * borrow_rate / periods
        cash -= borrow
        borrow_total += borrow
        if liquidate and i == len(opens) - 1:
            execute(-shares.copy(), close, timestamp, pd.NaT, "final_close")
        equity = cash + shares @ close
        if equity <= 0:
            raise ValueError(f"account insolvent at {timestamp}; performance is undefined")
        cash_rows.append(cash)
        equity_rows.append(equity)
        holding_rows.append(shares.copy())
    equity = pd.Series(equity_rows, index=opens.index, name="equity")
    cash_curve = pd.Series(cash_rows, index=opens.index, name="cash")
    account_returns = equity.pct_change(fill_method=None)
    account_returns.iloc[0] = equity.iloc[0] / initial_cash - 1
    benchmark = pd.Series(
        (initial_cash / opens.shape[1] / open_values[0]) @ close_values.T,
        index=opens.index,
        name="benchmark",
    )
    metrics = performance(account_returns, periods)
    metrics["commissions"] = fees_total
    metrics["borrow_costs"] = borrow_total
    metrics["fill_count"] = len(fills)
    metrics["benchmark_return"] = benchmark.iloc[-1] / initial_cash - 1
    trades = pd.DataFrame(
        fills, columns=["date", "signal_date", "asset", "quantity", "price", "commission", "phase"]
    )
    return BacktestResult(
        equity,
        cash_curve,
        pd.DataFrame(holding_rows, index=opens.index, columns=opens.columns),
        trades,
        account_returns,
        benchmark,
        metrics,
    )
