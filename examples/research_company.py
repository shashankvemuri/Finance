"""Estimate company value from statements and explicit growth scenarios. Add --live for AAPL."""

import sys

import pandas as pd

from finance.analytics import (
    company_cash_flows,
    company_scenarios,
    index_scenarios,
    statement_ratios,
)
from finance.data import YahooFinance


def main():
    if "--live" in sys.argv:
        provider = YahooFinance()
        income = provider.statements("AAPL", "income")
        cashflow = provider.statements("AAPL", "cashflow")
        print(statement_ratios(income, provider.statements("AAPL", "balance")).round(3))
        company = provider.company("AAPL")
        cash, debt, shares, price = (company[key] for key in ["cash", "debt", "shares", "price"])
    else:
        print("Synthetic financial statements; amounts in USD.")
        index = pd.to_datetime(["2023-12-31", "2024-12-31"])
        income = pd.DataFrame(
            {
                "Operating Income": [110e6, 132e6],
                "Tax Provision": [20e6, 24e6],
                "Pretax Income": [100e6, 120e6],
            },
            index=index,
        )
        cashflow = pd.DataFrame(
            {
                "Depreciation And Amortization": [10e6, 12e6],
                "Capital Expenditure": [-20e6, -25e6],
                "Change In Working Capital": [-5e6, -6e6],
            },
            index=index,
        )
        cash, debt, shares, price = 50e6, 100e6, 10e6, 100
    flows = company_cash_flows(income, cashflow)
    print("FCFF approximation by reported period:\n", flows.to_string())
    scenarios = {
        "slow": [0.02] * 5,
        "base": [0.08, 0.07, 0.06, 0.05, 0.04],
        "fast": [0.15, 0.12, 0.1, 0.08, 0.06],
    }
    print(
        company_scenarios(
            flows.fcff.iloc[-1], scenarios, 0.10, cash=cash, debt=debt, shares=shares, price=price
        )
        .round(2)
        .to_string()
    )
    print("Illustrative index EPS/payout assumptions:")
    print(
        index_scenarios(
            250,
            {"recovery": [-0.15, 0.2, 0.1, 0.05, 0.04], "slow": [0, 0.02, 0.03, 0.03, 0.03]},
            payout=0.4,
            discount_rate=0.09,
        ).round(2)
    )


if __name__ == "__main__":
    main()
