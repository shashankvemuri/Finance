from _data import load_prices

from finance.models import evaluate_arima, evaluate_forecast


def main():
    close = load_prices()["AAPL"].close
    print("Held-out errors; predictive skill is not assumed.")
    for result in [evaluate_forecast(close), evaluate_arima(close)]:
        print(f"Training ends {result.training_end}; test starts {result.test_start}")
        print(result.metrics.round(5).to_string())


if __name__ == "__main__":
    main()
