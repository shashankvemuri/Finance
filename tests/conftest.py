import numpy as np
import pandas as pd
import pytest


def pytest_addoption(parser):
    parser.addoption("--live", action="store_true", help="enable tests that contact data providers")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--live"):
        skip = pytest.mark.skip(reason="requires --live to contact data providers")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)


@pytest.fixture
def ohlcv():
    rng = np.random.default_rng(123)
    index = pd.bdate_range("2020-01-01", periods=600)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, len(index))))
    opening = close * np.exp(rng.normal(0, 0.003, len(index)))
    return pd.DataFrame(
        {
            "open": opening,
            "high": np.maximum(close, opening) * 1.01,
            "low": np.minimum(close, opening) * 0.99,
            "close": close,
            "volume": rng.integers(1000, 10000, len(index)).astype(float),
        },
        index=index,
    )
