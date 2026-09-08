"""Exercise the same UI actions users take; no network required."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest


def test_stock_and_portfolio_app(ohlcv):
    pytest.importorskip("streamlit")
    pytest.importorskip("scipy")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        str(Path(__file__).resolve().parents[1] / "apps/research.py"), default_timeout=30
    ).run()
    assert not app.exception
    with patch("finance.data.YahooFinance.history", return_value=ohlcv):
        app.button[0].click().run()
    assert not app.exception and len(app.dataframe) == 3
    app.sidebar.selectbox[0].set_value("Portfolio").run()
    frames = [ohlcv.copy() for _ in range(4)]
    # Different price paths avoid a singular, identical-asset optimization fixture.
    for i, frame in enumerate(frames):
        frame["close"] *= 1 + pd.Series(range(len(frame)), index=frame.index) * (i + 1) * 0.0001
    with patch("finance.data.YahooFinance.history", side_effect=frames):
        app.button[0].click().run()
    assert not app.exception and len(app.dataframe) == 2
    assert app.dataframe[0].value.weight.sum() == pytest.approx(1)
