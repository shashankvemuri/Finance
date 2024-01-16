import json
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
import datetime

# Set options for pandas display
pd.set_option('float_format', '{:f}'.format)

# API and stock configuration
base_url = "https://financialmodelingprep.com/api/v3/"
apiKey = "demo"  # Note: Demo API only works for AAPL stock
ticker = 'AAPL'
current_price = pdr.get_data_yahoo(ticker)['Adj Close'][-1]

# Function to retrieve JSON data from URL
def json_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# Retrieve financial statements
def get_financial_statements():
    # Income statement
    income = pd.DataFrame(json_data(f'{base_url}income-statement/{ticker}?apikey={apiKey}'))
    income = income.set_index('date').apply(pd.to_numeric, errors='coerce')

    # Cash flow statement
    cash_flow = pd.DataFrame(json_data(f'{base_url}cash-flow-statement/{ticker}?apikey={apiKey}'))
    cash_flow = cash_flow.set_index('date').apply(pd.to_numeric, errors='coerce')

    # Balance sheet
    balance_sheet = pd.DataFrame(json_data(f'{base_url}balance-sheet-statement/{ticker}?apikey={apiKey}'))
    balance_sheet = balance_sheet.set_index('date').apply(pd.to_numeric, errors='coerce')

    return income, cash_flow, balance_sheet

income, cash_flow, balance_sheet = get_financial_statements()

# Retrieve and process metrics from finviz
def get_finviz_data(ticker):
    url = f"http://finviz.com/quote.ashx?t={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    soup = bs(requests.get(url, headers=headers).content, features="lxml")

    metrics = ['Beta', 'EPS next 5Y', 'Shs Outstand']
    finviz_dict = {}
    for m in metrics:   
        finviz_dict[m] = soup.find(text=m).find_next(class_='snapshot-td2').text

    # Process and convert metrics to appropriate formats
    for key, value in finviz_dict.items():
        if value[-1] in ['%', 'B', 'M']:
            value = float(value[:-1])
            if value[-1] == 'B':
                value *= 1e9
            elif value[-1] == 'M':
                value *= 1e6
        finviz_dict[key] = float(value)
    return finviz_dict

finviz_data = get_finviz_data(ticker)
beta = finviz_data['Beta']

# Determine the discount rate based on beta
discount = 7 + beta * 2.5
if beta < 1:
    discount = 6

# Calculate intrinsic value
def calc_intrinsic_value(cash_flow, total_debt, liquid_assets, eps_growth_5Y, eps_growth_6Y_to_10Y, eps_growth_11Y_to_20Y, shs_outstanding, discount):   
    eps_growth_5Y /= 100
    eps_growth_6Y_to_10Y /= 100
    eps_growth_11Y_to_20Y /= 100
    discount /= 100

    cf_list = []
    for year in range(1, 21):
        growth_rate = eps_growth_5Y if year <= 5 else eps_growth_6Y_to_10Y if year <= 10 else eps_growth_11Y_to_20Y
        cash_flow *= (1 + growth_rate)
        discounted_cf = cash_flow / ((1 + discount)**year)
        cf_list.append(discounted_cf)

    intrinsic_value = (sum(cf_list) - total_debt + liquid_assets) / shs_outstanding
    return intrinsic_value

intrinsic_value = calc_intrinsic_value(cash_flow.iloc[-1]['freeCashFlow'],
                                       balance_sheet.iloc[-1]['totalDebt'],
                                       balance_sheet.iloc[-1]['cashAndShortTermInvestments'],
                                       finviz_data['EPS next 5Y'],
                                       finviz_data['EPS next 5Y'] / 2,
                                       np.minimum(finviz_data['EPS next 5Y'] / 2, 4),
                                       finviz_data['Shs Outstand'],
                                       discount)

# Calculate deviation from intrinsic value
percent_from_intrinsic_value = round((1 - current_price / intrinsic_value) * 100, 2)

# Display data in a DataFrame
data = {
    'Attributes': ['Intrinsic Value', 'Current Price', 'Intrinsic Value % from Price', 'Free Cash Flow', 'Total Debt', 'Cash and ST Investments', 'EPS Growth 5Y', 'EPS Growth 6Y to 10Y', 'EPS Growth 11Y to 20Y', 'Discount Rate', 'Shares Outstanding'],
    'Values': [intrinsic_value, current_price, percent_from_intrinsic_value, cash_flow.iloc[-1]['freeCashFlow'], balance_sheet.iloc[-1]['totalDebt'], balance_sheet.iloc[-1]['cashAndShortTermInvestments'], finviz_data['EPS next 5Y'], finviz_data['EPS next 5Y'] / 2, np.minimum(finviz_data['EPS next 5Y'] / 2, 4), discount, finviz_data['Shs Outstand']]
}
df = pd.DataFrame(data).set_index('Attributes')
print(df)