"""Forecast, diagnose and compare statistical experiments; --neural/--prophet need extras."""

import sys

from _data import load_prices

from finance.models import (
    arima_diagnostics,
    arima_forecast,
    evaluate_forecast,
    evaluate_prophet,
    evaluate_sequence,
    factor_analysis,
    forecast_latest,
    partial_correlations_cv,
    select_arima_order,
    student_t_fit,
    volatility_regimes,
)


def main():
    import pandas as pd

    prices = load_prices(("AAPL", "MSFT", "JPM", "SPY"))
    closes = pd.DataFrame({ticker: p.close for ticker, p in prices.items()})
    changes = closes.pct_change(fill_method=None).dropna()
    print(evaluate_forecast(closes.AAPL).metrics)
    print(forecast_latest(closes.AAPL).to_string())
    orders = select_arima_order(closes.AAPL)
    print(orders)
    print(arima_forecast(closes.AAPL, order=orders.order.iloc[0]))
    print(arima_diagnostics(closes.AAPL)[0])
    print(student_t_fit(changes.AAPL))
    print(factor_analysis(changes, 2).diagnostics)
    print(partial_correlations_cv(changes).round(3))
    print(volatility_regimes(closes.AAPL).tail())
    if "--neural" in sys.argv:
        for architecture in ["lstm", "cnn"]:
            print(evaluate_sequence(closes.AAPL, architecture=architecture).metrics)
    if "--prophet" in sys.argv:
        print(evaluate_prophet(closes.AAPL).metrics)


if __name__ == "__main__":
    main()
