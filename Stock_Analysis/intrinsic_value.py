# Importing required modules
import json
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
from yahoo_fin import stock_info as si

# Setting pandas options
pd.set_option('float_format', '{:f}'.format)

# API configuration
base_url = "https://financialmodelingprep.com/api/v3/"
apiKey = "demo" # demo api only works for AAPL stock

# Parameters
ticker = 'AAPL'  # The stock ticker to get its intrinsic value
current_price = si.get_live_price(ticker)

# Retrieving JSON data
def json_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# Income statement
income = pd.DataFrame(json_data(f'{base_url}income-statement/{ticker}?apikey={apiKey}'))
income = income.set_index('date')
income = income.apply(pd.to_numeric, errors='coerce')

# Last 4 quarters income statement
q_income = pd.DataFrame(json_data(f'{base_url}income-statement/{ticker}?period=quarter&apikey={apiKey}'))
q_income = q_income.set_index('date').iloc[:4] # extract for last 4 quarters
q_income = q_income.apply(pd.to_numeric, errors='coerce')

# Trailing twelve months income statement
ttm_income = q_income.sum()
ttm_income['netIncomeRatio'] = q_income['netIncomeRatio'][-1]
ttm_income['grossProfitRatio'] = q_income['grossProfitRatio'][-1]
ttm_income['ebitdaratio'] = q_income['ebitdaratio'][-1]
ttm_income['operatingIncomeRatio'] = q_income['operatingIncomeRatio'][-1]
income = income.iloc[::-1].append(ttm_income.rename('TTM'))

# Cash flow statement
cash_flow = pd.DataFrame(json_data(f'{base_url}cash-flow-statement/{ticker}?apikey={apiKey}'))
cash_flow = cash_flow.set_index('date')
cash_flow = cash_flow.apply(pd.to_numeric, errors='coerce')

# Last 4 quarters cash flow statement
q_cash_flow = pd.DataFrame(json_data(f'{base_url}cash-flow-statement/{ticker}?period=quarter&apikey={apiKey}'))
q_cash_flow = q_cash_flow.set_index('date').iloc[:4]
q_cash_flow = q_cash_flow.apply(pd.to_numeric, errors='coerce')

# Trailing twelve months cash flow statement
ttm_cash_flow = q_cash_flow.sum()
cash_flow = cash_flow.iloc[::-1].append(ttm_cash_flow.rename('TTM')).drop(['netIncome'], axis=1)

# Balance sheet
balance_sheet = pd.DataFrame(json_data(f'{base_url}balance-sheet-statement/{ticker}?apikey={apiKey}'))
balance_sheet = balance_sheet.set_index('date')
balance_sheet = balance_sheet.iloc[::-1].apply(pd.to_numeric, errors='coerce')

# Last 4 quarters balance sheet
q_balance_sheet = pd.DataFrame(json_data(f'{base_url}balance-sheet-statement/{ticker}?period=quarter&apikey={apiKey}'))
q_balance_sheet = q_balance_sheet.set_index('date').iloc[:4]
q_balance_sheet = q_balance_sheet.apply(pd.to_numeric, errors='coerce')
balance_sheet = balance_sheet.append(q_balance_sheet.iloc[0].rename('TTM'))

# Combining income, cash flow, and balance statements
all_sheets = pd.merge(income,cash_flow, how='outer', left_index=True, right_index=True)     
all_sheets = pd.merge(all_sheets,balance_sheet, how='outer', left_index=True, right_index=True)
all_sheets['Receivables-sales-ratio'] = all_sheets['netReceivables'] / all_sheets['revenue']

# Metrics of data needed from finviz.com
metrics = ['Beta', 'EPS next 5Y', 'Shs Outstand']

# Using beautifulsoup to find finviz metrics specified
def fundamental_metrics(soup, metrics):
    # Find the specified metric using the provided soup object and return the text
    return soup.find(text = metrics).find_next(class_='snapshot-td2').text
   
def get_finviz_data(ticker):
    try:
        # Generate the url for the given ticker and add headers to request
        url = (f"http://finviz.com/quote.ashx?t={ticker}")
        headers_dictionary = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
        
        # Use Beautifulsoup to parse the webpage
        soup = bs(requests.get(url,headers=headers_dictionary).content, features="lxml")
        
        # Create an empty dictionary to store the metrics and their values
        finviz_dict = {}
        
        # Loop through each metric in the list of metrics and find its value using the fundamental_metrics function
        for m in metrics:   
            finviz_dict[m] = fundamental_metrics(soup,m)
        
        # Loop through the dictionary and clean up the metric values by removing any text and converting to the appropriate number format
        for key, value in finviz_dict.items():
            # remove percentage sign and convert to float
            if (value[-1]=='%'):
                finviz_dict[key] = float(value[:-1])
            # convert billion to integer value
            if (value[-1]=='B'):
                finviz_dict[key] = float(value[:-1])*1000000000  
            # convert million to integer value
            if (value[-1]=='M'):
                finviz_dict[key] = float(value[:-1])*1000000
            
            # Convert the values to float if possible
            try:
                finviz_dict[key] = float(finviz_dict[key])
            except:
                pass 

    except Exception as e:
        print (f'The following error has occurred while retrieving finviz data \n{e}')        
    
    # Return the dictionary containing the finviz metrics
    return finviz_dict

# Retrieve beta value from the finviz data dictionary
finviz_data = get_finviz_data(ticker)
beta = finviz_data['Beta']

# Calculating discount rate based off beta value
discount = 7
if(beta<0.80):
    discount = 5
elif(beta>=0.80 and beta<1):
    discount = 6
elif(beta>=1 and beta<1.1):
    discount = 6.5
elif(beta>=1.1 and beta<1.2):
    discount = 7
elif(beta>=1.2 and beta<1.3):
    discount =7.5
elif(beta>=1.3 and beta<1.4):
    discount = 8
elif(beta>=1.4 and beta<1.6):
    discount = 8.5
elif(beta>=1.61):
    discount = 9   

# Creating variables from all sheets
cash_flow = all_sheets.iloc[-1]['freeCashFlow']
total_debt = all_sheets.iloc[-1]['totalDebt'] 
liquid_assets = all_sheets.iloc[-1]['cashAndShortTermInvestments']

# Retrieving and calculating further metrics from finviz
eps_growth_5Y = finviz_data['EPS next 5Y']
eps_growth_6Y_to_10Y = eps_growth_5Y/2
eps_growth_11Y_to_20Y  = np.minimum(eps_growth_6Y_to_10Y, 4)
shs_outstanding = finviz_data['Shs Outstand']

# Calclating instrinsic value using all metrics
def calc_intrinsic_value(cash_flow, total_debt, liquid_assets, 
                                  eps_growth_5Y, eps_growth_6Y_to_10Y, eps_growth_11Y_to_20Y,
                                  shs_outstanding, discount):   
    
    # Converting percentages to decmials
    eps_growth_5Y = eps_growth_5Y/100
    eps_growth_6Y_to_10Y = eps_growth_6Y_to_10Y/100
    eps_growth_11Y_to_20Y = eps_growth_11Y_to_20Y/100
    discount_d = discount/100
    
    # Projecting future cash flows
    cf_list = []
    
    # Cash Flows Years 1 to 5
    for year in range(1, 6):
        cash_flow*=(1 + eps_growth_5Y)
        cash_flow_discount = cash_flow/((1 + discount_d)**year)
        cf_list.append(cash_flow_discount)

    # Cash Flows Years 6 to 10        
    for year in range(6, 11):
        cash_flow*=(1 + eps_growth_6Y_to_10Y)
        cash_flow_discount = cash_flow/((1 + discount_d)**year)
        cf_list.append(cash_flow_discount)

    # Cash Flows Years 11 to 20
    for year in range(11, 21):
        cash_flow*=(1 + eps_growth_11Y_to_20Y)
        cash_flow_discount = cash_flow/((1 + discount_d)**year)
        cf_list.append(cash_flow_discount)
    
    intrinsic_value = (sum(cf_list) - total_debt + liquid_assets)/shs_outstanding

    return intrinsic_value

# Get intrinsic value
intrinsic_value = calc_intrinsic_value(cash_flow, total_debt, liquid_assets, 
                                  eps_growth_5Y, eps_growth_6Y_to_10Y, eps_growth_11Y_to_20Y,
                                  shs_outstanding, discount)    

# Current price deviation from intrinsic value
percent_from_instrinsic_value = round((1-current_price/intrinsic_value)*100, 2)

# Create and display dataframe with collected data
attrs = ["Intrinsic Value", "Current Price", "Intrinsic Value % from Price", "Free Cash Flow", "Total Debt", "Cash and ST Investments", "EPS Growth 5Y", "EPS Growth 6Y to 10Y", "EPS Growth 11Y to 20Y", "Discount Rate", "Shares Outstanding"]
values = [intrinsic_value, current_price, percent_from_instrinsic_value, cash_flow, total_debt, liquid_assets, eps_growth_5Y, eps_growth_6Y_to_10Y, eps_growth_11Y_to_20Y, shs_outstanding, discount]
data_tuples = list(zip(attrs,values))
df = pd.DataFrame(data_tuples, columns=['Attributes','Values'])
df.to_csv(f'{ticker}_intrinsic_value.csv')
print (df.set_index('Attributes'))