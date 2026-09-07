"""Opt-in provider contracts and numerical checks on real market data."""

import inspect
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

import finance.indicators as indicators
from finance.analytics import capm, discounted_cash_flow, net_positioning, returns, value_at_risk
from finance.backtesting import backtest
from finance.data import (
    YahooFinance,
    close_matrix,
    cot_financial_futures,
    dividend_calendar,
    exchange_universe,
    sp500_constituents,
)
from finance.models import evaluate_arima, evaluate_direction, evaluate_forecast
from finance.portfolio import efficient_frontier, optimize, simulate_portfolio
from finance.screening import minervini
from finance.strategies import moving_average, pairs_trade

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def provider():
    return YahooFinance()


@pytest.fixture(scope="module")
def prices(provider):
    return {
        ticker: provider.history(ticker, "2022-01-01", "2025-01-01")
        for ticker in ["AAPL", "MSFT", "NVDA", "JPM", "BAC", "SPY"]
    }


def test_indicators_screening_and_capm(prices):
    bars = prices["AAPL"]
    inputs = {**{k: bars[k] for k in bars}, "price": bars.close, "values": bars.close}
    for name in indicators.__all__:
        if name == "fibonacci_levels":
            continue
        function = getattr(indicators, name)
        parameters = inspect.signature(function).parameters
        if any(
            key not in inputs and parameter.default is inspect.Parameter.empty
            for key, parameter in parameters.items()
        ):
            continue
        arguments = {key: value for key, value in inputs.items() if key in parameters}
        if name == "pivot_points":
            arguments.pop("open", None)
        values = function(**arguments)
        assert values.index.equals(bars.index), name
        assert values.notna().to_numpy().any(), name
        assert not np.isinf(values.to_numpy()).any(), name
    assert indicators.rsi(bars.close).dropna().between(0, 100).all()
    screen = minervini({k: v for k, v in prices.items() if k != "SPY"}, prices["SPY"].close)
    assert screen.rs_rank.between(0, 100).all()
    changes = returns(close_matrix(prices)).dropna()
    result = capm(changes.AAPL, changes.SPY)
    beta, alpha = np.polyfit(changes.SPY, changes.AAPL, 1)
    assert np.isclose(beta, result.beta)
    assert np.isclose(alpha * 252, result.alpha)


def test_backtest_accounting(prices):
    bars = prices["AAPL"]
    result = backtest(
        bars.open, bars.close, moving_average(bars.close), commission=0.001, slippage=0.0005
    )
    assert not result.trades.empty
    cash, shares = 10000.0, 0.0
    # Reconstruct cash and shares independently from the public fill journal.
    for row in result.trades.itertuples():
        assert row.signal_date < row.date
        assert row.price > 0
        cash -= row.quantity * row.price + row.commission
        shares += row.quantity
    final = cash + shares * bars.close.iloc[-1]
    assert np.isclose(final, result.equity.iloc[-1])
    assert np.isclose(np.prod(1 + result.returns), final / 10000)
    assert result.cash.min() >= -1e-7
    opens = pd.DataFrame({k: prices[k].open for k in ["JPM", "BAC"]})
    closes = close_matrix(prices)[["JPM", "BAC"]]
    targets = pairs_trade(closes.JPM, closes.BAC).set_axis(closes.columns, axis=1)
    pair = backtest(opens, closes, targets, borrow_rate=0.03)
    assert np.allclose(pair.equity, pair.cash + (pair.holdings * closes).sum(axis=1))


def test_optimization_and_simulation(prices):
    changes = returns(close_matrix(prices)).dropna()
    mean, cov = changes.mean() * 252, changes.cov() * 252
    for objective in ["minimum_variance", "maximum_sharpe"]:
        allocation = optimize(mean, cov, objective=objective, bounds=(0, 0.5))
        assert np.isclose(allocation.weights.sum(), 1)
        assert allocation.weights.between(-1e-7, 0.5000001).all()
        weights = allocation.weights.reindex(mean.index).to_numpy()
        assert np.isclose(weights @ mean, allocation.statistics["return"])
        assert np.isclose(
            np.sqrt(weights @ cov.to_numpy() @ weights), allocation.statistics.volatility
        )
    frontier = efficient_frontier(mean, cov, 20)
    assert len(frontier) == 20 and np.isfinite(frontier).all().all()
    paths = simulate_portfolio(allocation.weights, mean, cov, paths=10000, steps=60)
    assert paths.shape == (61, 10000) and (paths > 0).all().all()
    expected = 10000 * (allocation.weights.reindex(mean.index) @ np.exp(mean))
    assert abs(paths.iloc[-1].mean() - expected) / expected < 0.02
    assert 0 <= value_at_risk(paths.iloc[-1] / 10000 - 1) <= 1


@pytest.mark.parametrize("model", ["ridge", "forest", "boosting", "svr", "mlp"])
def test_forecast_evaluation(prices, model):
    result = evaluate_forecast(prices["AAPL"].close, model=model, horizon=5)
    assert result.training_end < result.test_start
    assert result.predictions.notna().all().all()
    assert np.isclose(
        result.metrics.loc["zero_return", "mae"], result.predictions.actual.abs().mean()
    )
    assert np.isfinite(result.metrics).all().all()


def test_time_series_and_direction_evaluation(prices):
    close = prices["AAPL"].close
    forecast = evaluate_arima(close)
    assert {"arima", "persistence"} <= set(forecast.metrics.index)
    assert np.isfinite(forecast.metrics).all().all()
    direction = evaluate_direction(close)
    assert direction.predictions.gaussian_nb.between(0, 1).all()
    assert direction.metrics.brier.between(0, 1).all()


@pytest.mark.parametrize("method", ["company", "earnings", "insider_transactions", "news"])
def test_company_providers(provider, method):
    data = getattr(provider, method)("AAPL")
    assert not data.empty


def test_dividends_and_valuation(provider):
    dividends = provider.dividends("AAPL", "2024-01-01", "2025-01-01")
    assert len(dividends) == 4 and (dividends > 0).all()
    dividend = provider.company("AAPL").annual_dividend
    # Per-share dividends use equity discounting, with no enterprise cash/debt adjustments.
    flows = np.array([dividend * 1.04**year for year in range(1, 6)])
    valuation = discounted_cash_flow(flows, 0.08, 0.025)
    expected = (flows / 1.08 ** np.arange(1, 6)).sum() + flows[-1] * 1.025 / (
        0.08 - 0.025
    ) / 1.08**5
    assert valuation.value_per_share > 0
    assert np.isclose(valuation.value_per_share, expected)


@pytest.mark.parametrize("fetch", [sp500_constituents, exchange_universe])
def test_market_universes(fetch):
    data = fetch()
    assert len(data) >= 500


def test_dividend_calendar():
    data = dividend_calendar(date.today().isoformat())
    # An empty calendar is valid on holidays and days without scheduled dividends.
    assert "ticker" in data.columns


def test_intraday(provider):
    end = date.today()
    start = end - timedelta(days=14)
    bars = provider.history("AAPL", start.isoformat(), end.isoformat(), interval="5m")
    assert len(bars) > 100 and bars.index.is_monotonic_increasing
    assert (bars.close > 0).all()


def test_cftc_positioning():
    data = cot_financial_futures("13874A", "2023-01-01", "2025-01-01")
    assert len(data) >= 100
    net = net_positioning(
        data.lev_money_positions_long, data.lev_money_positions_short, data.open_interest_all
    )
    assert net.between(-1, 1).all()
