from finance.analytics import discounted_cash_flow, scenario_valuation


def main():
    # Illustrative USD millions; unlevered cash flows and shares in millions.
    flows = [100, 108, 116, 123, 130]
    result = discounted_cash_flow(flows, 0.10, 0.025, cash=50, debt=200, shares=100)
    print(f"Enterprise value: ${result.enterprise_value:.2f} million")
    print(f"Equity value per share: ${result.value_per_share:.2f}")
    scenarios = {"base": flows, "down": [x * 0.8 for x in flows], "up": [x * 1.2 for x in flows]}
    print(scenario_valuation(scenarios, [0.08, 0.10, 0.12]).round(2).to_string())


if __name__ == "__main__":
    main()
