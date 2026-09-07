import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from finance.analytics import (
    capm,
    cumulative_returns,
    discounted_cash_flow,
    drawdown,
    expected_shortfall,
    kelly_fraction,
    ols,
    performance,
    period_returns,
    pnl,
    position_size,
    returns,
    risk_reward,
    scenario_valuation,
    value_at_risk,
)


def test_returns_compound_and_missing():
    price = pd.Series([100.0, 110, 99])
    assert_allclose(returns(price).iloc[1:], [0.1, -0.1])
    assert cumulative_returns(returns(price).dropna()).iloc[-1] == pytest.approx(-0.01)
    assert returns(pd.Series([100.0, np.nan, 120])).isna().all()
    assert_allclose(returns(price, log=True).iloc[1:], np.log([1.1, 0.9]))
    assert_allclose(pnl(price, 2, 100, 1), [-1, 19, -3])


def test_drawdown_includes_initial_loss():
    stats = performance(pd.Series([-0.1, 0.05]), periods=2)
    assert stats.max_drawdown == pytest.approx(-0.1)
    assert stats.total_return == pytest.approx(-0.055)
    assert stats.cagr == pytest.approx(-0.055)
    assert_allclose(drawdown(pd.Series([90.0, 100, 80]), initial=100), [-0.1, 0, -0.2])


def test_var_loss_convention_and_kelly():
    r = pd.Series([-0.2, -0.1, 0, 0.1, 0.2])
    assert value_at_risk(r, 0.8) == pytest.approx(0.12)
    assert expected_shortfall(r, 0.8) == 0.2
    assert value_at_risk(pd.Series([0.1, 0.2, 0.3])) == 0
    assert value_at_risk(pd.Series([-1.0, 0, 1]), 0.975, method="normal") == pytest.approx(
        1.9599639845
    )
    assert kelly_fraction(0.6, 2) == pytest.approx(0.4)
    assert risk_reward(100, 95, 110) == 2
    assert risk_reward(100, 105, 90, short=True) == 2
    assert position_size(10000, 0.01, 100, 95) == 20


def test_dcf_independent_perpetuity_identity():
    # Flat $100 annual cash flows forever discounted at 10% are worth $1,000 today.
    result = discounted_cash_flow([100] * 5, 0.1, 0, cash=50, debt=100, shares=10)
    assert result.enterprise_value == pytest.approx(1000)
    assert result.equity_value == pytest.approx(950)
    assert result.value_per_share == pytest.approx(95)
    assert result.present_values.iloc[0] == pytest.approx(100 / 1.1)
    assert result.present_values.sum() + result.terminal_present_value == result.enterprise_value
    scenarios = scenario_valuation({"base": [100] * 5, "up": [110] * 5}, [0.08, 0.1], 0)
    assert scenarios.loc[0.1, "up"] == pytest.approx(1100)
    with pytest.raises(ValueError):
        discounted_cash_flow([100], 0.02, 0.03)


def test_ols_capm_against_known_equation():
    x = pd.Series([-0.02, 0.03, 0.01, -0.01, 0.04])
    y = 0.001 + 1.5 * x
    result = ols(y, x.to_frame("market"))
    assert_allclose(result.coefficients, [0.001, 1.5], atol=1e-14)
    assert result.r_squared == pytest.approx(1)
    assert_allclose(result.residuals, 0, atol=1e-14)
    report = capm(y, x)
    assert report.beta == pytest.approx(1.5)
    assert report.alpha == pytest.approx(0.252)
    with pytest.raises(ValueError):
        ols(y, pd.DataFrame({"a": x, "b": 2 * x}))


def test_period_returns_are_period_changes():
    p = pd.Series(
        [100.0, 110, 121, 133.1],
        index=pd.to_datetime(["2023-01-31", "2023-02-28", "2023-03-31", "2023-04-28"]),
    )
    assert_allclose(period_returns(p), 0.1)


@pytest.mark.parametrize("bad", [pd.Series([1.0, np.inf]), pd.Series([1.0, np.nan])])
def test_invalid_returns_rejected(bad):
    with pytest.raises(ValueError):
        performance(bad)
