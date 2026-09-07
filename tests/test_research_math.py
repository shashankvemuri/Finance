import numpy as np
import pandas as pd
import pytest

from finance.analytics import company_cash_flows, company_scenarios, seasonal_entries
from finance.backtesting import backtest, completed_trades, trade_statistics
from finance.indicators import gann_fan, natr, speed_resistance
from finance.screening import green_line_screen, growth_screen
from finance.strategies import ichimoku_trend, keltner_breakout, macd_trend, select_strategy


def bars(opening, high, low, close):
    index = pd.date_range("2024-01-01", periods=len(opening))
    return pd.DataFrame(
        {"open": opening, "high": high, "low": low, "close": close, "volume": 1000},
        index=index,
        dtype=float,
    )


@pytest.mark.parametrize("short", [False, True])
def test_gap_stop_and_no_reentry(short):
    p = bars([100, 100, 80, 100], [101, 101, 101, 101], [99, 99, 79, 99], [100, 100, 100, 100])
    if short:
        p = bars([100, 100, 120, 100], [101, 101, 121, 101], [99, 99, 99, 99], [100, 100, 100, 100])
    target = pd.Series(-1.0 if short else 1.0, index=p.index)
    r = backtest(
        p.open, p.close, target, high_prices=p.high, low_prices=p.low, stop_loss=0.1, commission=0
    )
    assert r.equity.iloc[-1] == pytest.approx(8000)
    assert len(r.trades) == 2
    assert r.trades.iloc[-1].phase == "stop"
    assert r.trades.iloc[-1].price == (120 if short else 80)
    assert r.holdings.iloc[-1, 0] == 0


def test_ambiguous_stop_first_and_known_trailing_level():
    p = bars([100, 100, 100], [101, 125, 101], [99, 85, 99], [100, 100, 100])
    target = pd.Series(1.0, index=p.index)
    r = backtest(
        p.open,
        p.close,
        target,
        high_prices=p.high,
        low_prices=p.low,
        stop_loss=0.1,
        take_profit=0.2,
        commission=0,
    )
    assert r.trades.iloc[-1].price == 90
    # Same-bar high cannot retrospectively raise the stop before the low happened.
    r = backtest(
        p.open,
        p.close,
        target,
        high_prices=p.high,
        low_prices=p.low,
        trailing_fraction=0.2,
        commission=0,
    )
    assert r.trades.iloc[-1].date == p.index[2]
    assert r.trades.iloc[-1].price == 100


def test_stops_prefix_causal_and_accounting(ohlcv):
    target = pd.Series(np.where(np.arange(len(ohlcv)) % 60 < 30, 1.0, -1.0), index=ohlcv.index)

    def run(p, t):
        return backtest(
            p.open,
            p.close,
            t,
            high_prices=p.high,
            low_prices=p.low,
            stop_loss=0.03,
            take_profit=0.06,
            trailing_fraction=0.04,
            borrow_rate=0.02,
        )

    full, short = run(ohlcv, target), run(ohlcv.iloc[:300], target.iloc[:300])
    pd.testing.assert_series_equal(full.equity.iloc[:300], short.equity)
    pd.testing.assert_series_equal(
        full.equity, (full.cash + full.holdings.iloc[:, 0] * ohlcv.close).rename("equity")
    )
    matched = completed_trades(full.trades)
    realized = matched.net_pnl.sum()
    # Liquidation provides an independent full-cash reconciliation of matched lots and borrow.
    closed = backtest(
        ohlcv.open, ohlcv.close, target, commission=0.001, borrow_rate=0.02, liquidate=True
    )
    assert completed_trades(
        closed.trades
    ).net_pnl.sum() - closed.metrics.borrow_costs == pytest.approx(closed.equity.iloc[-1] - 10000)
    assert np.isfinite(realized)


def test_fifo_partial_close_reversal_fees():
    fills = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=4),
            "asset": "A",
            "quantity": [10, -4, -10, 4],
            "price": [100, 110, 90, 80],
            "commission": [1, 0.4, 1, 0.4],
        }
    )
    matched = completed_trades(fills)
    assert matched.quantity.tolist() == [4, 6, 4]
    assert matched.gross_pnl.tolist() == [40, -60, 40]
    assert matched.net_pnl.sum() == pytest.approx(17.2)
    assert matched.commission.sum() == pytest.approx(fills.commission.sum())
    assert trade_statistics(matched).win_rate == pytest.approx(2 / 3)


def test_fcff_interest_tax_sign_and_perpetuity():
    income = pd.DataFrame(
        {"Operating Income": [100.0], "Tax Provision": [20.0], "Pretax Income": [100.0]}
    )
    cf = pd.DataFrame(
        {
            "Depreciation And Amortization": [50.0],
            "Capital Expenditure": [-30.0],
            "Change In Working Capital": [-2.0],
        }
    )
    assert company_cash_flows(income, cf).fcff.iloc[0] == 98
    result = company_scenarios(
        100, {"flat": [0] * 5}, 0.1, terminal_growth=0, cash=50, debt=100, shares=10, price=100
    )
    assert result.value_per_share.iloc[0] == pytest.approx(95)
    assert result.upside.iloc[0] == pytest.approx(-0.05)
    with pytest.raises(ValueError):
        company_cash_flows(income, cf.assign(**{"Capital Expenditure": 30}))


def test_seasonal_dates_and_incomplete_holds():
    close = pd.Series(np.arange(800) + 100.0, index=pd.bdate_range("2022-01-01", periods=800))
    result = seasonal_entries(close, 1, 15, 1)
    row = result.iloc[0]
    assert row.entry == pd.Timestamp("2022-01-17")
    assert row.exit == pd.Timestamp("2022-02-17")
    assert row["return"] == pytest.approx(close.loc[row.exit] / close.loc[row.entry] - 1)
    assert (result.exit <= close.index[-1]).all()


def test_growth_missing_fields_and_green_line(ohlcv):
    c = pd.DataFrame(
        {
            "earnings_growth": [0.2, 0.2],
            "revenue_growth": [0.2, np.nan],
            "profit_margin": [0.2, 0.2],
            "institutional_transactions": [0.1, 0.1],
            "pe": [20, 20],
        }
    )
    assert growth_screen(c).passed.tolist() == [True, False]
    result = green_line_screen({"A": ohlcv})
    assert result.index.tolist() == ["A"]
    assert result.passed.iloc[0] == (abs(result.distance.iloc[0]) <= 0.05)


def test_drawings_hand_values_and_warmup(ohlcv):
    fan = gann_fan(5, 100, 2)
    assert fan["1"].tolist() == [100, 102, 104, 106, 108]
    speed = speed_resistance(100, 130, 3, 6)
    assert speed.iloc[:3].isna().all().all()
    assert speed["1"].iloc[3] == 130
    values = natr(ohlcv.high, ohlcv.low, ohlcv.close)
    assert values.iloc[:13].isna().all()
    assert (values.dropna() > 0).all()


@pytest.mark.parametrize(
    "strategy",
    [
        lambda p: macd_trend(p.close),
        lambda p: keltner_breakout(p.high, p.low, p.close),
        lambda p: ichimoku_trend(p.high, p.low, p.close),
    ],
)
def test_new_signals_prefix(strategy, ohlcv):
    pd.testing.assert_series_equal(strategy(ohlcv).iloc[:200], strategy(ohlcv.iloc[:200]))


def test_selection_holdout_cannot_change_selection(ohlcv):
    prices = ohlcv.iloc[:120].copy()
    candidates = {
        "long": lambda p: pd.Series(1.0, index=p.index),
        "flat": lambda p: pd.Series(0.0, index=p.index),
    }
    first = select_strategy(prices, candidates)
    changed = prices.copy()
    changed.loc[changed.index[84:], ["open", "high", "low", "close"]] *= 2
    second = select_strategy(changed, candidates)
    assert first.selected == second.selected
    pd.testing.assert_frame_equal(first.training_scores, second.training_scores)
    assert first.holdout.equity.index[0] == first.test_start
    assert first.holdout.benchmark.iloc[0] == pytest.approx(
        10000 * prices.close.iloc[84] / prices.open.iloc[84]
    )


def test_latest_incomplete_fcff_is_not_silently_replaced():
    income = pd.DataFrame(
        {
            "Operating Income": [100.0, 100.0],
            "Tax Provision": [20.0, 20.0],
            "Pretax Income": [100.0, 100.0],
        }
    )
    cash = pd.DataFrame(
        {
            "Depreciation And Amortization": [5.0, np.nan],
            "Capital Expenditure": [-10.0, -10.0],
            "Change In Working Capital": [0.0, 0.0],
        }
    )
    with pytest.raises(ValueError, match="latest common"):
        company_cash_flows(income, cash)


def test_pivot_midpoints_are_between_levels(ohlcv):
    from finance.indicators import pivot_midpoints, pivot_points

    pivots = pivot_points(ohlcv.high, ohlcv.low, ohlcv.close)
    middle = pivot_midpoints(pivots)
    pd.testing.assert_series_equal(
        middle.s1_pivot, ((pivots.s1 + pivots["pivot"]) / 2).rename("s1_pivot")
    )
