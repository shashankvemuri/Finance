"""Explicit live integration run, independent accounting checks, and a saved numerical report."""

import inspect
import json
from pathlib import Path

import numpy as np
import pandas as pd

import finance.indicators as indicators
from finance.analytics import (
    capm,
    discounted_cash_flow,
    net_positioning,
    returns,
    sentiment,
    value_at_risk,
)
from finance.backtesting import backtest
from finance.data import (
    YahooFinance,
    close_matrix,
    cot_financial_futures,
    dividend_calendar,
    exchange_universe,
    sp500_constituents,
)
from finance.models import (
    anomaly_scores,
    cluster_assets,
    cluster_features,
    cointegration_pairs,
    evaluate_arima,
    evaluate_direction,
    evaluate_forecast,
    partial_correlations,
    pca,
)
from finance.portfolio import efficient_frontier, optimize, simulate_portfolio
from finance.screening import fundamental_screen, minervini, rsi_screen, technical_screen
from finance.strategies import moving_average, pairs_trade


def main():
    provider = YahooFinance()
    tickers = ["AAPL", "MSFT", "NVDA", "JPM", "BAC", "SPY"]
    prices = {ticker: provider.history(ticker, "2022-01-01", "2025-01-01") for ticker in tickers}
    closes = close_matrix(prices)
    changes = returns(closes).dropna()
    report = {
        "period": ["2022-01-01", "2025-01-01"],
        "rows": {k: len(v) for k, v in prices.items()},
    }
    bars = prices["AAPL"]
    report["indicators"] = {}
    inputs = {**{k: bars[k] for k in bars}, "price": bars.close, "values": bars.close}
    for name in indicators.__all__:
        if name == "fibonacci_levels":
            continue
        fn = getattr(indicators, name)
        parameters = inspect.signature(fn).parameters
        if any(
            k not in inputs and p.default is inspect.Parameter.empty for k, p in parameters.items()
        ):
            continue
        args = {k: v for k, v in inputs.items() if k in parameters}
        if name == "pivot_points":
            args.pop("open", None)
        values = fn(**args)
        assert values.index.equals(bars.index) and values.notna().to_numpy().any()
        assert not np.isinf(values.to_numpy()).any()
        last = values.iloc[-1]
        report["indicators"][name] = last.to_dict() if isinstance(last, pd.Series) else float(last)
    oscillator = indicators.rsi(bars.close).dropna()
    assert oscillator.between(0, 100).all()
    report["rsi_range"] = [float(oscillator.min()), float(oscillator.max())]
    screen = minervini({k: v for k, v in prices.items() if k != "SPY"}, prices["SPY"].close)
    assert screen.rs_rank.between(0, 100).all()
    report["minervini"] = screen.reset_index().to_dict("records")
    report["rsi_screen"] = rsi_screen(closes).to_dict()
    report["technical_screen"] = technical_screen(bars.close).to_dict()
    result = backtest(
        bars.open, bars.close, moving_average(bars.close), commission=0.001, slippage=0.0005
    )
    # Independently reconstruct ledger, without using the backtest's positions or cash code.
    cash, shares = 10000.0, 0.0
    for row in result.trades.itertuples():
        assert row.signal_date < row.date
        assert row.price > 0
        cash -= row.quantity * row.price + row.commission
        shares += row.quantity
    final = cash + shares * bars.close.iloc[-1]
    assert np.isclose(final, result.equity.iloc[-1])
    assert np.isclose(np.prod(1 + result.returns), final / 10000)
    assert result.cash.min() >= -1e-7
    report["backtest"] = result.metrics.to_dict()
    report["backtest"]["reconstructed_final_equity"] = final
    report["fills"] = result.trades.tail(5).astype(str).to_dict("records")
    opens = pd.DataFrame({k: prices[k].open for k in ["JPM", "BAC"]})
    pair_closes = closes[["JPM", "BAC"]]
    target = pairs_trade(pair_closes.JPM, pair_closes.BAC).set_axis(pair_closes.columns, axis=1)
    pair = backtest(opens, pair_closes, target, borrow_rate=0.03)
    assert np.allclose(pair.equity, pair.cash + (pair.holdings * pair_closes).sum(axis=1))
    report["pairs_experiment"] = pair.metrics.to_dict()
    mean, cov = changes.mean() * 252, changes.cov() * 252
    report["portfolios"] = {}
    for objective in ["minimum_variance", "maximum_sharpe"]:
        allocation = optimize(mean, cov, objective=objective, bounds=(0, 0.5))
        assert np.isclose(allocation.weights.sum(), 1)
        assert allocation.weights.between(-1e-7, 0.5000001).all()
        w = allocation.weights.reindex(mean.index).to_numpy()
        assert np.isclose(w @ mean, allocation.statistics["return"])
        assert np.isclose(np.sqrt(w @ cov.to_numpy() @ w), allocation.statistics.volatility)
        report["portfolios"][objective] = {
            "weights": allocation.weights.to_dict(),
            "statistics": allocation.statistics.to_dict(),
        }
    report["frontier"] = efficient_frontier(mean, cov, 6).to_dict("records")
    paths = simulate_portfolio(allocation.weights, mean, cov, paths=10000, steps=60)
    assert paths.shape == (61, 10000) and (paths > 0).all().all()
    expected = 10000 * (allocation.weights.reindex(mean.index) @ np.exp(mean))
    report["simulation"] = {
        "mean": paths.iloc[-1].mean(),
        "analytical_mean": expected,
        "var95": value_at_risk(paths.iloc[-1] / 10000 - 1),
    }
    assert abs(paths.iloc[-1].mean() - expected) / expected < 0.02
    capm_result = capm(changes.AAPL, changes.SPY)
    beta, alpha = np.polyfit(changes.SPY, changes.AAPL, 1)
    assert np.isclose(beta, capm_result.beta) and np.isclose(alpha * 252, capm_result.alpha)
    report["capm"] = capm_result.to_dict()
    report["models"] = {}
    for model in ["ridge", "forest", "boosting", "svr", "mlp"]:
        result = evaluate_forecast(bars.close, model=model, horizon=5)
        assert result.training_end < result.test_start
        report["models"][model] = {
            "metrics": result.metrics.to_dict(),
            "training_end": str(result.training_end),
            "test_start": str(result.test_start),
        }
    report["models"]["arima"] = evaluate_arima(bars.close).metrics.to_dict()
    report["models"]["gaussian_nb"] = evaluate_direction(bars.close).metrics.to_dict()
    structure = pca(changes, 3)
    assert np.allclose(structure.loadings.T @ structure.loadings, np.eye(3))
    report["pca_explained_variance"] = structure.explained_variance.to_dict()
    report["clusters"] = cluster_assets(changes, 3, components=2).to_dict()
    report["mixture_clusters"] = cluster_assets(
        changes, 3, components=2, method="mixture"
    ).to_dict()
    features = pd.DataFrame(
        {"rsi": closes.apply(lambda x: indicators.rsi(x).iloc[-1]), "volatility": changes.std()}
    ).sort_index()
    report["feature_clusters"] = cluster_features(features, 3).to_dict()
    report["cointegration_training_only"] = cointegration_pairs(closes.iloc[:400]).to_dict(
        "records"
    )
    report["anomaly_range"] = (
        anomaly_scores(changes.iloc[:400], changes.iloc[400:]).agg(["min", "max"]).to_dict()
    )
    partial = partial_correlations(changes)
    assert np.allclose(partial, partial.T) and (abs(partial) <= 1 + 1e-10).all().all()
    report["partial_correlations"] = partial.to_dict()
    report["providers"] = {}
    for name, fn in [
        ("company", lambda: provider.company("AAPL")),
        ("dividends", lambda: provider.dividends("AAPL", "2024-01-01", "2025-01-01")),
        ("earnings", lambda: provider.earnings("AAPL")),
        ("insider", lambda: provider.insider_transactions("AAPL")),
        ("news", lambda: provider.news("AAPL")),
        ("sp500", sp500_constituents),
        ("exchanges", exchange_universe),
        ("calendar", lambda: dividend_calendar("2026-09-04")),
        ("intraday", lambda: provider.history("AAPL", "2026-09-01", "2026-09-05", interval="5m")),
        ("cot", lambda: cot_financial_futures("13874A", "2023-01-01", "2025-01-01")),
    ]:
        data = fn()
        assert not data.empty
        report["providers"][name] = {"shape": list(data.shape), "sample": data.head(2).to_string()}
        if name == "cot":
            net = net_positioning(
                data.lev_money_positions_long,
                data.lev_money_positions_short,
                data.open_interest_all,
            )
            assert net.between(-1, 1).all()
            report["cot_net_range"] = net.agg(["min", "max"]).to_dict()
    company = provider.company("AAPL")
    report["fundamental_screen"] = fundamental_screen(company.to_frame().T).to_dict()
    # Current dividend-per-share scenario, not an unlevered DCF using after-interest Yahoo FCF.
    dividend = company.annual_dividend
    valuation = discounted_cash_flow([dividend * 1.04**i for i in range(1, 6)], 0.08, 0.025)
    assert valuation.value_per_share > 0
    report["dividend_valuation"] = {
        "annual_dividend": dividend,
        "scenario_value": valuation.value_per_share,
        "assumptions": "4% dividend growth for 5 years, 8% equity discount, 2.5% terminal growth; illustrative",
    }
    report["sentiment"] = sentiment(
        ["Record profit and excellent growth.", "Terrible losses and bankruptcy."]
    ).to_dict("records")
    path = Path(__file__).parent / "live_verification.json"
    path.write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(
        f"Live verification complete: {len(report['indicators'])} indicators, {len(report['providers'])} provider workflows. Saved {path}"
    )
    print(pd.Series(report["backtest"]).to_string())


if __name__ == "__main__":
    main()
