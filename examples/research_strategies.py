"""Compare signal families on a chronological holdout and inspect stop-aware trades."""

from _data import load_prices

from finance.analytics import seasonal_summary
from finance.backtesting import backtest, completed_trades, trade_statistics
from finance.screening import green_line_screen, rsi_trend_screen
from finance.strategies import (
    ichimoku_trend,
    keltner_breakout,
    macd_trend,
    moving_average,
    select_strategy,
    stochastic_reversion,
    williams_reversion,
)


def main():
    prices = load_prices()["AAPL"]
    candidates = {
        "ma": lambda p: moving_average(p.close),
        "macd": lambda p: macd_trend(p.close),
        "keltner": lambda p: keltner_breakout(p.high, p.low, p.close),
        "stochastic": lambda p: stochastic_reversion(p.high, p.low, p.close),
        "williams": lambda p: williams_reversion(p.high, p.low, p.close),
        "ichimoku": lambda p: ichimoku_trend(p.high, p.low, p.close),
    }
    selection = select_strategy(prices, candidates, stop_losses=(None, 0.05, 0.1))
    print(
        "Training scores:",
        selection.training_scores[["candidate", "stop_loss", "total_return", "max_drawdown"]].round(
            3
        ),
    )
    print(
        "Selected:", selection.selected, "Holdout:", selection.holdout.metrics.round(3).to_string()
    )
    result = backtest(
        prices.open,
        prices.close,
        moving_average(prices.close, short=True),
        high_prices=prices.high,
        low_prices=prices.low,
        stop_loss=0.08,
        trailing_fraction=0.1,
        take_profit=0.2,
        liquidate=True,
    )
    print(trade_statistics(completed_trades(result.trades)).to_string())
    print(green_line_screen({"AAPL": prices}).to_string())
    print(rsi_trend_screen(prices[["close"]]).to_string())
    print(seasonal_summary(prices[["close"]], 1, 15, 3).to_string())


if __name__ == "__main__":
    main()
