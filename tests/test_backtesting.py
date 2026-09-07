import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from finance.backtesting import backtest
from finance.strategies import moving_average, pairs_trade, trailing_stop


def s(values):
    return pd.Series(values, index=pd.date_range("2024-01-01", periods=len(values)), dtype=float)


def test_next_open_and_cash_by_hand():
    result = backtest(
        s([10, 20, 30, 40]), s([15, 25, 35, 45]), s([1, 0, 0, 1]), initial_cash=100, commission=0
    )
    # Buy 5 at second open (20), sell 5 at third open (30). Last signal never executes.
    assert_allclose(result.equity, [100, 125, 150, 150])
    assert_allclose(result.cash, [100, 0, 150, 150], atol=1e-12)
    assert_allclose(result.holdings.asset, [0, 5, 0, 0])
    assert_allclose(result.trades.price, [20, 30])
    assert result.metrics.total_return == pytest.approx(0.5)
    assert (result.trades.signal_date < result.trades.date).all()


def test_short_sale_proceeds_and_borrow_by_hand():
    result = backtest(
        s([10, 10, 8, 8]),
        s([10, 8, 8, 8]),
        s([-1, 0, 0, 0]),
        initial_cash=100,
        commission=0,
        borrow_rate=0.252,
    )
    assert_allclose(result.holdings.asset, [0, -10, 0, 0])
    assert_allclose(result.cash, [100, 199.9, 119.9, 119.9])
    assert_allclose(result.equity, [100, 119.9, 119.9, 119.9])
    assert result.metrics.borrow_costs == pytest.approx(0.1)


def test_costs_no_overspend_and_exact_reconciliation():
    result = backtest(
        s([10, 10, 10, 10]),
        s([10, 10, 10, 10]),
        s([1, 0, 0, 0]),
        initial_cash=100,
        commission=0.01,
        slippage=0.02,
    )
    shares = 100 / (10 * 1.02 * 1.01)
    expected = shares * 10 * 0.98 * 0.99
    assert result.equity.iloc[-1] == pytest.approx(expected)
    assert result.cash.min() >= -1e-10
    cash = 100.0
    quantity = 0.0
    for row in result.trades.itertuples():
        cash -= row.quantity * row.price + row.commission
        quantity += row.quantity
    assert cash + quantity * 10 == pytest.approx(expected)
    assert (1 + result.returns).prod() == pytest.approx(expected / 100)


def test_reversal_and_two_assets():
    price = s([10] * 5)
    result = backtest(price, price, s([1, -1, 0, 0, 0]), commission=0, initial_cash=100)
    assert_allclose(result.trades.quantity, [10, -20, 10])
    assert_allclose(result.equity, 100)
    prices = pd.DataFrame({"a": s([10, 10, 12, 12]), "b": s([20, 20, 18, 18])})
    targets = pd.DataFrame({"a": s([0.5, 0.5, 0, 0]), "b": s([-0.5, -0.5, 0, 0])})
    result = backtest(prices, prices, targets, commission=0, initial_cash=100)
    assert result.equity.iloc[-1] == pytest.approx(115)
    assert_allclose(result.equity, result.cash + (result.holdings * prices).sum(axis=1))


def test_prefix_invariance_and_last_liquidation(ohlcv):
    targets = moving_average(ohlcv.close)
    result = backtest(ohlcv.open, ohlcv.close, targets)
    prefix = backtest(ohlcv.open.iloc[:300], ohlcv.close.iloc[:300], targets.iloc[:300])
    assert_allclose(result.equity.iloc[:300], prefix.equity)
    liquidated = backtest(
        ohlcv.open, ohlcv.close, pd.Series(1.0, index=ohlcv.index), liquidate=True
    )
    assert_allclose(liquidated.holdings.iloc[-1], 0, atol=1e-12)
    assert liquidated.trades.iloc[-1].phase == "final_close"


def test_insolvency_and_bad_targets():
    with pytest.raises(ValueError, match="insolvent"):
        backtest(s([10, 10, 40]), s([10, 10, 40]), s([-1, -1, -1]), commission=0)
    with pytest.raises(ValueError, match="gross"):
        backtest(s([10, 10]), s([10, 10]), s([2, 2]))
    with pytest.raises(ValueError):
        backtest(s([10, 10]), s([10, 10]), s([np.nan, 1]))


def test_pairs_and_stops(ohlcv):
    pair = pairs_trade(ohlcv.close, ohlcv.close * 1.1)
    assert_allclose(pair.sum(axis=1), 0)
    assert (pair.abs().sum(axis=1) <= 1).all()
    targets = trailing_stop(s([100, 110, 98, 120, 125, 130]), s([1, 1, 1, 1, 0, 1]), 0.1)
    assert_allclose(targets, [1, 1, 0, 0, 0, 1])
