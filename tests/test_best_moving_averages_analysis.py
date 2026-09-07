import contextlib
import io
import runpy
import unittest
from pathlib import Path
from unittest.mock import ANY, patch

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "portfolio_strategies"
    / "best_moving_averages_analysis.py"
)
SYMBOL = "TSLA"


def make_flat_prices():
    index = pd.bdate_range("2022-01-03", periods=900)
    trend = np.linspace(100.0, 220.0, len(index))
    cycle = 4.0 * np.sin(np.arange(len(index)) / 11.0)
    close = trend + cycle
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.full(len(index), 1_000_000.0),
        },
        index=index,
    )


def to_multiindex(frame, tickers=(SYMBOL,)):
    columns = pd.MultiIndex.from_product(
        [frame.columns, tickers],
        names=["Price", "Ticker"],
    )
    values = np.column_stack(
        [
            frame[column].to_numpy()
            for column in frame.columns
            for _ticker in tickers
        ]
    )
    return pd.DataFrame(values, index=frame.index, columns=columns)


def make_malformed_multiindex_prices():
    flat = make_flat_prices()
    current = to_multiindex(flat)

    three_level_columns = pd.MultiIndex.from_tuples(
        [
            (price, ticker, interval)
            for price, ticker in current.columns
            for interval in ("1d",)
        ],
        names=["Price", "Ticker", "Interval"],
    )
    three_level_values = np.column_stack(
        [
            current[(price, ticker)].to_numpy()
            for price, ticker in current.columns
            for _interval in ("1d",)
        ]
    )
    three_level = pd.DataFrame(
        three_level_values,
        index=flat.index,
        columns=three_level_columns,
    )

    duplicate_level_names = current.copy(deep=True)
    duplicate_level_names.columns = duplicate_level_names.columns.set_names(
        ["Ticker", "Ticker"]
    )

    duplicate_close_columns = pd.DataFrame(
        np.column_stack([current.to_numpy(), flat["Close"].to_numpy()]),
        index=flat.index,
        columns=pd.MultiIndex.from_tuples(
            [*current.columns, ("Close", SYMBOL)],
            names=["Price", "Ticker"],
        ),
    )

    return {
        "three levels": three_level,
        "duplicate level names": duplicate_level_names,
        "multiple tickers": to_multiindex(flat, tickers=(SYMBOL, "AAPL")),
        "unexpected single ticker": to_multiindex(flat, tickers=("AAPL",)),
        "duplicate flattened Close columns": duplicate_close_columns,
        "missing Close": to_multiindex(flat.drop(columns=["Close"])),
    }


def run_script(frame):
    with (
        patch("yfinance.download", return_value=frame.copy(deep=True)) as download,
        patch("matplotlib.pyplot.show"),
        contextlib.redirect_stdout(io.StringIO()),
    ):
        try:
            namespace = runpy.run_path(str(SCRIPT_PATH))
        finally:
            plt.close("all")
    return namespace, download


class BestMovingAveragesCompatibilityTests(unittest.TestCase):
    def test_accepts_legacy_and_current_single_ticker_columns(self):
        flat = make_flat_prices()
        fixtures = {
            "legacy flat columns": flat,
            "current MultiIndex columns": to_multiindex(flat),
            "ticker-first MultiIndex columns": to_multiindex(flat).swaplevel(
                axis="columns"
            ),
        }

        expected_results = None
        for name, frame in fixtures.items():
            with self.subTest(name=name):
                namespace, download = run_script(frame)

                self.assertNotIsInstance(namespace["data"].columns, pd.MultiIndex)
                self.assertTrue(namespace["data"].columns.is_unique)
                self.assertIsInstance(namespace["data"]["Close"], pd.Series)
                download.assert_called_once_with(
                    SYMBOL,
                    start=ANY,
                    end=ANY,
                    auto_adjust=False,
                )
                results = pd.DataFrame(namespace["results"])
                if expected_results is None:
                    expected_results = results
                else:
                    pd.testing.assert_frame_equal(results, expected_results)

    def test_rejects_malformed_multiindex_columns(self):
        for name, frame in make_malformed_multiindex_prices().items():
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    ValueError,
                    "single-ticker yfinance columns",
                ):
                    run_script(frame)

    def test_legacy_flat_missing_close_keeps_key_error(self):
        flat_missing_close = make_flat_prices().drop(columns=["Close"])

        with self.assertRaises(KeyError):
            run_script(flat_missing_close)


if __name__ == "__main__":
    unittest.main()
