"""Opt-in checks against public sources; provider failures are failures, never empty successes."""

import numpy as np
import pandas as pd
import pytest

from finance.analytics import company_cash_flows, sentence_sentiment
from finance.data import (
    Finviz,
    TradingView,
    YahooFinance,
    article_text,
    earnings_calendar,
    rss_news,
    transcript_index,
)

pytestmark = pytest.mark.integration


def test_live_finviz_discovery_and_company():
    f = Finviz()
    screen = f.screen(["cap_largeover", "fa_epsqoq_o10"], limit=40)
    assert len(screen) == 40 and screen.index.is_unique
    assert screen.market_cap.ge(1e10).all()
    company = f.company("AAPL")
    assert company.price > 0 and 0 <= company.rsi <= 100
    assert company.market_cap > 1e11
    assert company["low_52w"] <= company.price <= company["high_52w"]
    assert len(f.analysts("AAPL")) > 0
    assert len(f.insiders()) > 0
    assert f.news("AAPL").url.str.startswith("http").all()


def test_live_market_calendars_and_universe():
    f = Finviz()
    assert len(f.universe("dow")) == 30
    result = f.market()
    assert len(result["movers"]) > 0 and len(result["futures"]) > 0
    earnings = earnings_calendar("2026-09-04", "2026-09-05")
    assert len(earnings) > 0 and earnings.ticker.notna().all()


def test_live_statements_and_fcff():
    provider = YahooFinance()
    income, cash = provider.statements("AAPL", "income"), provider.statements("AAPL", "cashflow")
    result = company_cash_flows(income, cash)
    assert result.index[-1] == income.index[-1]
    assert result.fcff.iloc[-1] > 0 and np.isfinite(result.fcff).all()
    period = result.index[-1]
    tax = income.loc[period, "Tax Provision"] / income.loc[period, "Pretax Income"]
    expected = (
        income.loc[period, "Operating Income"] * (1 - tax)
        + cash.loc[
            period,
            ["Depreciation And Amortization", "Capital Expenditure", "Change In Working Capital"],
        ].sum()
    )
    assert result.fcff.iloc[-1] == pytest.approx(expected)


def test_live_news_transcript_and_vendor_recommendations():
    feed = rss_news("https://feeds.content.dowjones.io/public/rss/mw_topstories")
    assert len(feed) > 0 and isinstance(feed.published.dtype, pd.DatetimeTZDtype)
    index = transcript_index()
    text = article_text(index.url.iloc[0])
    assert len(text) > 1000
    scores = sentence_sentiment(text)
    assert scores.compound.between(-1, 1).all()
    recommendations = TradingView().recommendations(["NASDAQ:AAPL", "NASDAQ:MSFT"])
    assert recommendations.drop(columns="price").abs().le(1).all().all()
