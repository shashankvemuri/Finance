import numpy as np
import pandas as pd
years=['2019A', '2020F', '2021F', '2022F', '2023F', '2024F']
sales = pd.Series(index=years)

sales['2019A'] = 15
growth_rate = 0.1
ebitda_margin = 0.20
depr_percent = 0.03
tax_rate = 0.30
nwc_percent = 0.24
cost_of_capital = 0.10
terminal_growth = 0.02

# Loop to populate the data series of sales
for year in range(1,6):
    sales[year] = sales[year-1] * (1+growth_rate)
    
ebitda = sales * ebitda_margin
depreciation = sales * depr_percent
ebit = ebitda - depreciation
tax_payment = -ebit * tax_rate
tax_payment = tax_payment.apply(lambda x: min(x,0))
nopat = ebit + tax_payment
print('nopat:')
print(nopat)

nwc = sales * nwc_percent
change_in_nwc = nwc.shift(1) - nwc
capex_percent = depr_percent
capex = -(sales * capex_percent)

free_cash_flow = nopat + depreciation + capex + change_in_nwc
print('\nfree cash flow:')
print (free_cash_flow)

terminal_value = ((free_cash_flow[-1] * (1 + terminal_growth))/
                 (cost_of_capital - terminal_growth))
discount_factors = [(1 / (1 + cost_of_capital)) ** i for i in range (1,6)]
dcf_value = (sum(free_cash_flow[1:]*discount_factors) +
            terminal_value * discount_factors[-1])
print('\ndcf_value: ',dcf_value)

# Exporting the Data to Excel
output = pd.DataFrame([sales, ebit, tax_payment, nopat, 
                       depreciation, capex, change_in_nwc,
                       free_cash_flow],
                     index=["Sales", "EBIT", "Tax Expense", 
                            "NOPAT", "D&A Expense",
                            "Capital Expenditures",
                            "Increase in NWC",
                            "Free Cash Flow"]).round(2)
print('\nOutput: ')
print(output)