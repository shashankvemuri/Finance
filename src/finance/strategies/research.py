from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from finance.analytics import performance
from finance.backtesting import BacktestResult, backtest
from finance.data import normalize_ohlcv
from finance.indicators import ichimoku, keltner, macd, stochastic, williams_r
from finance.strategies.signals import crossover, threshold_reversion


def macd_trend(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9, *, short: bool = False
) -> pd.Series:
    values = macd(close, fast, slow, signal)
    return crossover(values.macd, values.signal, short=short)


def stochastic_reversion(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14, *, short: bool = False
) -> pd.Series:
    values = stochastic(high, low, close, window)
    return threshold_reversion(values.k, 20, 80, 50, short=short)


def williams_reversion(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14, *, short: bool = False
) -> pd.Series:
    return threshold_reversion(williams_r(high, low, close, window), -80, -20, -50, short=short)


def keltner_breakout(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 20,
    multiplier: float = 2,
    *,
    short: bool = False,
) -> pd.Series:
    bands = keltner(high, low, close, window, multiplier=multiplier)
    state, values = 0.0, []
    for price, lower, middle, upper in zip(
        close, bands.lower, bands.middle, bands.upper, strict=True
    ):
        if (state > 0 and price < middle) or (state < 0 and price > middle):
            state = 0.0
        elif state == 0:
            state = 1.0 if price > upper else -1.0 if short and price < lower else 0.0
        values.append(state)
    return pd.Series(values, index=close.index, name="target")


def ichimoku_trend(
    high: pd.Series, low: pd.Series, close: pd.Series, *, short: bool = False
) -> pd.Series:
    values = ichimoku(high, low)
    # Spans calculated 26 bars earlier form the cloud visible at the current bar.
    cloud = values[["span_a", "span_b"]].shift(26)
    above = (close > cloud.max(axis=1, skipna=False)) & (values.conversion > values.base)
    below = (close < cloud.min(axis=1, skipna=False)) & (values.conversion < values.base)
    return pd.Series(
        np.select([above, below], [1.0, -1.0 if short else 0.0], 0.0),
        index=close.index,
        name="target",
    )


@dataclass(frozen=True)
class StrategySelection:
    training_scores: pd.DataFrame
    selected: str
    holdout: BacktestResult
    training_end: object
    test_start: object


def select_strategy(
    prices: pd.DataFrame,
    candidates: dict[str, Callable],
    *,
    train_fraction: float = 0.7,
    commission: float = 0.001,
    metric: str = "total_return",
    stop_losses: tuple[float | None, ...] = (None,),
) -> StrategySelection:
    """Rank training performance, execute one untouched holdout; callbacks receive observed history."""
    if metric not in ("total_return", "sharpe", "sortino"):
        raise ValueError("metric must be total_return, sharpe or sortino")
    prices = normalize_ohlcv(prices)
    if not candidates or not 0.2 < train_fraction < 0.9:
        raise ValueError("provide candidates and a split in (.2,.9)")
    split = int(len(prices) * train_fraction)
    if split < 60 or len(prices) - split < 20:
        raise ValueError("insufficient train/holdout history")
    training = prices.iloc[:split]
    if not stop_losses or any(
        x is not None and (not np.isfinite(x) or not 0 < x < 1) for x in stop_losses
    ):
        raise ValueError("stop_losses must contain None or fractions in (0,1)")
    scores = []
    for name, strategy in candidates.items():
        targets = strategy(training.copy())
        for stop in stop_losses:
            result = backtest(
                training.open,
                training.close,
                targets,
                commission=commission,
                liquidate=True,
                high_prices=training.high,
                low_prices=training.low,
                stop_loss=stop,
            )
            scores.append({"candidate": name, "stop_loss": stop, **result.metrics.to_dict()})
    table = pd.DataFrame(scores).sort_values(metric, ascending=False, ignore_index=True)
    if not np.isfinite(table[metric].iloc[0]):
        raise ValueError("no candidate has a finite training score")
    selected = table.candidate.iloc[0]
    stop_loss = table.stop_loss.iloc[0]
    stop_loss = None if pd.isna(stop_loss) else float(stop_loss)
    # Evaluate each decision on a prefix, so callbacks cannot inspect future bars.
    targets = [
        candidates[selected](prices.iloc[: i + 1].copy()).iloc[-1]
        for i in range(split - 1, len(prices))
    ]
    evaluation = prices.iloc[split - 1 :]
    result = backtest(
        evaluation.open,
        evaluation.close,
        pd.Series(targets, index=evaluation.index),
        commission=commission,
        liquidate=True,
        high_prices=evaluation.high,
        low_prices=evaluation.low,
        stop_loss=stop_loss,
    )
    # Drop the signal-only seed bar from holdout performance and benchmark timing.
    equity = result.equity.iloc[1:]
    benchmark = (10000 / prices.open.iloc[split] * prices.close.iloc[split:]).rename("benchmark")
    metrics = performance(result.returns.iloc[1:])
    for key in ("commissions", "borrow_costs", "fill_count"):
        metrics[key] = result.metrics[key]
    metrics["benchmark_return"] = benchmark.iloc[-1] / 10000 - 1
    result = replace(
        result,
        equity=equity,
        cash=result.cash.iloc[1:],
        holdings=result.holdings.iloc[1:],
        returns=result.returns.iloc[1:],
        benchmark=benchmark,
        metrics=metrics,
    )
    return StrategySelection(table, selected, result, training.index[-1], prices.index[split])
