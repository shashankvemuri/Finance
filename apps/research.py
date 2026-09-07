"""Run with: streamlit run apps/research.py"""

import pandas as pd
import streamlit as st

from finance.analytics import company_cash_flows, company_scenarios, sentiment
from finance.backtesting import backtest, completed_trades, trade_statistics
from finance.data import Finviz, ProviderError, YahooFinance, fetch_many
from finance.indicators import bollinger_bands, cci, ema, macd, obv, rsi, sma
from finance.portfolio import optimize
from finance.reports import candles, equity_chart
from finance.screening import growth_screen
from finance.strategies import moving_average


def main():
    st.set_page_config(page_title="Finance research", layout="wide")
    st.title("Finance research")
    area = st.sidebar.selectbox(
        "Research",
        ["Stock & strategy", "Discover stocks", "Company valuation", "News", "Portfolio"],
    )
    ticker = st.sidebar.text_input("Ticker", "AAPL").strip().upper()
    if area == "Stock & strategy":
        with st.form("stock"):
            start = st.date_input("Start", pd.Timestamp("2023-01-01"))
            end = st.date_input("End (exclusive)", pd.Timestamp.today())
            overlays = st.multiselect(
                "Indicators",
                ["SMA", "EMA", "Bollinger", "MACD", "RSI", "CCI", "OBV"],
                default=["SMA", "Bollinger"],
            )
            fast = st.number_input("Fast average", min_value=2, value=20)
            slow = st.number_input("Slow average", min_value=3, value=50)
            submitted = st.form_submit_button("Analyze")
        if submitted:
            prices = YahooFinance().history(ticker, str(start), str(end))
            lines = pd.DataFrame(index=prices.index)
            if "SMA" in overlays:
                lines["SMA"] = sma(prices.close)
            if "EMA" in overlays:
                lines["EMA"] = ema(prices.close)
            if "Bollinger" in overlays:
                lines = lines.join(bollinger_bands(prices.close).add_prefix("BB "))
            st.pyplot(candles(prices.tail(120), lines.tail(120)))
            for name in overlays:
                if name == "MACD":
                    st.line_chart(macd(prices.close))
                elif name == "RSI":
                    st.line_chart(rsi(prices.close))
                elif name == "CCI":
                    st.line_chart(cci(prices.high, prices.low, prices.close))
                elif name == "OBV":
                    st.line_chart(obv(prices.close, prices.volume))
            result = backtest(
                prices.open, prices.close, moving_average(prices.close, fast, slow), liquidate=True
            )
            st.pyplot(equity_chart(result))
            st.dataframe(result.metrics.to_frame("value"))
            trades = completed_trades(result.trades)
            st.dataframe(trade_statistics(trades).to_frame("value"))
            st.dataframe(trades)
    elif area == "Discover stocks":
        if st.button("Screen 20 large growth companies"):
            f = Finviz()
            discovery = f.screen(["cap_largeover", "fa_epsqoq_o10"], limit=20)
            st.caption(
                f"First 20 of {discovery.attrs['total_matches']} matches; current snapshots."
            )
            batch = fetch_many(discovery.index, f.company)
            if not batch.errors.empty:
                st.warning(batch.errors.to_string())
            if batch.data:
                st.dataframe(growth_screen(batch.table()))
    elif area == "Company valuation":
        growth = st.slider("Annual FCFF growth", -0.1, 0.3, 0.05)
        discount = st.slider("Discount rate", 0.04, 0.2, 0.1)
        terminal = st.slider("Terminal growth", 0.0, 0.05, 0.025)
        if st.button("Value company"):
            provider = YahooFinance()
            flows = company_cash_flows(
                provider.statements(ticker, "income"), provider.statements(ticker, "cashflow")
            )
            info = provider.company(ticker)
            st.caption(
                "FCFF uses after-tax operating income, depreciation, capex and working capital. Review inputs and dilution."
            )
            st.dataframe(flows)
            st.dataframe(
                company_scenarios(
                    flows.fcff.iloc[-1],
                    {"assumptions": [growth] * 5},
                    discount,
                    terminal_growth=terminal,
                    cash=info.cash,
                    debt=info.debt,
                    shares=info.shares,
                    price=info.price,
                )
            )
    elif area == "News":
        if st.button("Read headlines"):
            news = Finviz().news(ticker)
            st.dataframe(news)
            scores = sentiment(news.title.tolist())
            st.dataframe(scores[["text", "compound"]])
            st.caption("Language sentiment describes headlines; it does not forecast returns.")
    else:
        symbols = st.text_input("Portfolio tickers", "AAPL MSFT JPM SPY").split()
        if st.button("Find minimum variance allocation"):
            provider = YahooFinance()
            close = pd.DataFrame(
                {
                    s: provider.history(s, "2023-01-01", str(pd.Timestamp.today().date())).close
                    for s in symbols
                }
            ).dropna()
            changes = close.pct_change(fill_method=None).dropna()
            result = optimize(changes.mean() * 252, changes.cov() * 252)
            st.dataframe(result.weights.to_frame("weight"))
            st.dataframe(close.pct_change(fill_method=None).corr())
            st.caption("Historical estimates; allocation is sensitive to the selected sample.")


if __name__ == "__main__":
    try:
        main()
    except (ProviderError, ValueError) as exc:
        st.error(str(exc))
