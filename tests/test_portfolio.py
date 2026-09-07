import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from finance.portfolio import (
    discrete_allocation,
    efficient_frontier,
    geometric_brownian_motion,
    lump_sum_vs_dca,
    optimize,
    portfolio_returns,
    portfolio_statistics,
    random_allocations,
    simulate_portfolio,
)


def inputs():
    return pd.Series([0.08, 0.12], index=["a", "b"]), pd.DataFrame(
        [[0.04, 0], [0, 0.09]], index=["a", "b"], columns=["a", "b"]
    )


def test_minimum_variance_analytic_reference():
    pytest.importorskip("scipy")
    mean, cov = inputs()
    result = optimize(mean, cov)
    # Two independent assets: inverse-variance weights, derived from first-order condition.
    assert_allclose(result.weights, [0.09 / 0.13, 0.04 / 0.13], atol=1e-6)
    assert result.statistics.volatility == pytest.approx(np.sqrt(0.04 * 0.09 / 0.13))
    assert result.statistics["return"] == pytest.approx(result.weights @ mean)
    sharpe = optimize(mean, cov, objective="maximum_sharpe")
    analytical = np.linalg.solve(cov, mean)
    analytical /= analytical.sum()
    assert_allclose(sharpe.weights, analytical, atol=1e-5)
    bound = optimize(mean, cov, bounds=(0.4, 0.6))
    assert_allclose(bound.weights, [0.6, 0.4], atol=1e-6)
    frontier = efficient_frontier(mean, cov, 5)
    assert len(frontier) == 5
    assert_allclose(frontier[["weight_a", "weight_b"]].sum(axis=1), 1)
    with pytest.raises(ValueError):
        optimize(mean, cov, target_return=0.5)


def test_portfolio_label_alignment_and_covariance_validation():
    mean, cov = inputs()
    weights = pd.Series({"b": 0.5, "a": 0.5})
    report = portfolio_statistics(weights, mean, cov)
    assert report["return"] == pytest.approx(0.1)
    assert report.volatility == pytest.approx(np.sqrt(0.0325))
    with pytest.raises(ValueError):
        portfolio_statistics(weights, mean, cov.assign(b=[1, 1]))
    with pytest.raises(ValueError):
        portfolio_statistics(weights * 2, mean, cov)
    asset_returns = pd.DataFrame({"a": [0.1, -0.1], "b": [-0.1, 0.1]})
    assert_allclose(portfolio_returns(asset_returns, weights), 0)
    allocation, cash = discrete_allocation(weights, pd.Series({"a": 30.0, "b": 40.0}), 100)
    assert_allclose(allocation, [1, 1])
    assert cash == 30


def test_simulation_analytical_moments_and_reproducibility():
    paths = geometric_brownian_motion(100, 0.05, 0.2, steps=50, paths=40000, seed=8)
    assert paths.shape == (51, 40000)
    assert_allclose(paths.iloc[0], 100)
    assert paths.to_numpy().min() > 0
    terminal = paths.iloc[-1]
    assert terminal.mean() == pytest.approx(100 * np.exp(0.05), rel=0.004)
    expected_variance = 100**2 * np.exp(0.1) * (np.exp(0.04) - 1)
    assert terminal.var() == pytest.approx(expected_variance, rel=0.025)
    deterministic = geometric_brownian_motion(100, 0.1, 0, steps=5, paths=3)
    assert_allclose(deterministic.iloc[-1], 100 * np.exp(0.1))
    mean, cov = inputs()
    weights = pd.Series({"a": 0.4, "b": 0.6})
    result = simulate_portfolio(weights, mean, cov, paths=20000, steps=12, seed=1)
    assert result.iloc[-1].mean() == pytest.approx(10000 * (weights @ np.exp(mean)), rel=0.006)
    assert_allclose(result.iloc[0], 10000)
    a = simulate_portfolio(weights, mean, cov, paths=5, steps=5, seed=5)
    b = simulate_portfolio(weights, mean, cov, paths=5, steps=5, seed=5)
    assert_allclose(a, b)


def test_cashflows_and_random_allocations():
    result = lump_sum_vs_dca(pd.Series([10.0, 10, 10, 10]), 100, 4)
    assert_allclose(result, 100)
    result = lump_sum_vs_dca(pd.Series([10.0, 20]), 100, 2)
    assert result.dca.iloc[-1] == 150
    assert result.lump_sum.iloc[-1] == 200
    mean, cov = inputs()
    random = random_allocations(mean, cov, 100)
    assert_allclose(random[["a", "b"]].sum(axis=1), 1)
    assert_allclose(random["return"], random[["a", "b"]] @ mean)


def test_frontier_endpoints_and_redundant_target():
    pytest.importorskip("scipy")
    mean, cov = inputs()
    assert_allclose(optimize(mean, cov, target_return=mean.max()).weights, [0, 1], atol=1e-9)
    assert_allclose(optimize(mean, cov, target_return=mean.min()).weights, [1, 0], atol=1e-9)
    same_return = mean * 0 + 0.1
    allocation = optimize(same_return, cov, target_return=0.1)
    assert_allclose(allocation.weights, [0.09 / 0.13, 0.04 / 0.13], atol=1e-6)
    assert_allclose(efficient_frontier(same_return, cov, 3)["return"], 0.1)
