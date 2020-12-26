# Code from https://medium.com/datadriveninvestor/use-python-to-evaluate-a-stock-investment-7ef09effd426 by Bohmian

# Importing required modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [15, 10]
import numpy as np
import seaborn as sns
from config import financial_model_prep

# To extract and parse fundamental data from finviz website
import requests
from bs4 import BeautifulSoup as bs

# For parsing financial statements data from financialmodelingprep api
from urllib.request import urlopen
import json
def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# Financialmodelingprep api url
base_url = "https://financialmodelingprep.com/api/v3/"

# apiKey = "demo" # demo api only works for AAPL stock
apiKey = financial_model_prep()
ticker = input('Enter a ticker: ')

income_statement = pd.DataFrame(get_jsonparsed_data(base_url+'income-statement/' + ticker + '?apikey=' + apiKey))
income_statement = income_statement.set_index('date')
income_statement = income_statement.apply(pd.to_numeric, errors='coerce')

q_income_statement = pd.DataFrame(get_jsonparsed_data(base_url+'income-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
q_income_statement = q_income_statement.set_index('date').iloc[:4] # extract for last 4 quarters
q_income_statement = q_income_statement.apply(pd.to_numeric, errors='coerce')

ttm_income_statement = q_income_statement.sum() # sum up last 4 quarters to get TTM cash flow

ttm_income_statement['netIncomeRatio'] = q_income_statement['netIncomeRatio'][-1]
ttm_income_statement['grossProfitRatio'] = q_income_statement['grossProfitRatio'][-1]
ttm_income_statement['ebitdaratio'] = q_income_statement['ebitdaratio'][-1]
ttm_income_statement['operatingIncomeRatio'] = q_income_statement['operatingIncomeRatio'][-1]
income_statement = income_statement.iloc[::-1].append(ttm_income_statement.rename('TTM'))

cash_flow_statement = pd.DataFrame(get_jsonparsed_data(base_url+'cash-flow-statement/' + ticker + '?apikey=' + apiKey))
cash_flow_statement = cash_flow_statement.set_index('date')
cash_flow_statement = cash_flow_statement.apply(pd.to_numeric, errors='coerce')
    
q_cash_flow_statement = pd.DataFrame(get_jsonparsed_data(base_url+'cash-flow-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
q_cash_flow_statement = q_cash_flow_statement.set_index('date').iloc[:4]
q_cash_flow_statement = q_cash_flow_statement.apply(pd.to_numeric, errors='coerce')

ttm_cash_flow_statement = q_cash_flow_statement.sum()
cash_flow_statement = cash_flow_statement.iloc[::-1].append(ttm_cash_flow_statement.rename('TTM')).drop(['netIncome'], axis=1)

balance_statement = pd.DataFrame(get_jsonparsed_data(base_url+'balance-sheet-statement/' + ticker + '?apikey=' + apiKey))
balance_statement = balance_statement.set_index('date')
balance_statement = balance_statement.iloc[::-1].apply(pd.to_numeric, errors='coerce')

q_balance_statement = pd.DataFrame(get_jsonparsed_data(base_url+'balance-sheet-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
q_balance_statement = q_balance_statement.set_index('date').iloc[:4]
q_balance_statement = q_balance_statement.apply(pd.to_numeric, errors='coerce')
balance_statement = balance_statement.append(q_balance_statement.iloc[0].rename('TTM'))

all_statements = pd.merge(income_statement,cash_flow_statement, how='outer', left_index=True, right_index=True)     
all_statements = pd.merge(all_statements,balance_statement, how='outer', left_index=True, right_index=True)
all_statements['Receivables-sales-ratio'] = all_statements['netReceivables'] / all_statements['revenue']

all_statements[['revenue', 'operatingCashFlow', 'netIncome']].plot(kind='bar', title=ticker + ' Revenue, Cash Flow, Income, Receivables (All Must Increase)')
plt.show()

all_statements[['operatingCashFlow', 'netIncome']].plot(kind='bar', title=ticker + ' Above Without Revenue (Clearer Scale) (All Must Increase)')
plt.show()

all_statements[['operatingCashFlow', 'capitalExpenditure', 'freeCashFlow']].plot(kind='bar', title=ticker + ' Cash Flow Situation')
plt.show()

print("Return on Equity should be 12% to 15%")    
all_statements['ROE'] = all_statements['netIncome'] / all_statements['totalStockholdersEquity']
all_statements['ROE'].plot(kind='bar', title=ticker + ' ROE (should be above 10%)')    
plt.show()

all_statements['grossProfitMargin'] = (all_statements['revenue'] - all_statements['costOfRevenue']) / all_statements['revenue']
all_statements['grossProfitMargin'].plot(kind='bar', title=ticker + ' Gross Profit Margin')    
plt.show()

all_statements['netProfitMargin'] = all_statements['netIncome'] / all_statements['revenue']
all_statements['netProfitMargin'].plot(kind='bar', title=ticker + ' Net Profit Margin')    
plt.show()

print("Current assets / current liabilities ratio should be > 1.")    
all_statements['Current-Ratio'] = all_statements['totalCurrentAssets'] / all_statements['totalCurrentLiabilities']
all_statements['Current-Ratio'].plot(kind='bar', title=ticker + ' Current Ratio (Must Be Consistent and Greater Than 1)')    
plt.show()

print("Debt servicing ratio should be < 0.2.")   
all_statements['Debt-Servicing-Ratio'] = all_statements['interestExpense'] / all_statements['operatingCashFlow']
all_statements['Debt-Servicing-Ratio'].plot(kind='bar', title=ticker + ' Debt Servicing Ratio (< 0.2)')    
plt.show()

# List of data we want to extract from Finviz Table
metric = ['Price', 'EPS next 5Y', 'Beta', 'Shs Outstand']

def fundamental_metric(soup, metric):
    # the table which stores the data in Finviz has html table attribute class of 'snapshot-td2'
    return soup.find(text = metric).find_next(class_='snapshot-td2').text
   
def get_finviz_data(ticker):
    try:
        url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
        soup = bs(requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}).content, features="lxml")
        dict_finviz = {}        
        for m in metric:   
            dict_finviz[m] = fundamental_metric(soup,m)
        for key, value in dict_finviz.items():
            # replace percentages
            if (value[-1]=='%'):
                dict_finviz[key] = value[:-1]
                dict_finviz[key] = float(dict_finviz[key])
            # billion
            if (value[-1]=='B'):
                dict_finviz[key] = value[:-1]
                dict_finviz[key] = float(dict_finviz[key])*1000000000  
            # million
            if (value[-1]=='M'):
                dict_finviz[key] = value[:-1]
                dict_finviz[key] = float(dict_finviz[key])*1000000
            try:
                dict_finviz[key] = float(dict_finviz[key])
            except:
                pass 
    except Exception as e:
        print (e)
        print ('Not successful parsing ' + ticker + ' data.')        
    return dict_finviz

finviz_data = get_finviz_data(ticker)

Beta = finviz_data['Beta']

discount_rate = 7
if(Beta<0.80):
    discount_rate = 5
elif(Beta>=0.80 and Beta<1):
    discount_rate = 6
elif(Beta>=1 and Beta<1.1):
    discount_rate = 6.5
elif(Beta>=1.1 and Beta<1.2):
    discount_rate = 7
elif(Beta>=1.2 and Beta<1.3):
    discount_rate =7.5
elif(Beta>=1.3 and Beta<1.4):
    discount_rate = 8
elif(Beta>=1.4 and Beta<1.6):
    discount_rate = 8.5
elif(Beta>=1.61):
    discount_rate = 9   

cash_flow = all_statements.iloc[-1]['freeCashFlow']
total_debt = all_statements.iloc[-1]['totalDebt'] 
cash_and_ST_investments = all_statements.iloc[-1]['cashAndShortTermInvestments']

EPS_growth_5Y = finviz_data['EPS next 5Y']
EPS_growth_6Y_to_10Y = EPS_growth_5Y/2  # Half the previous growth rate, conservative estimate
EPS_growth_11Y_to_20Y  = np.minimum(EPS_growth_6Y_to_10Y, 4)  # Slightly higher than long term inflation rate, conservative estimate
shares_outstanding = finviz_data['Shs Outstand']

print("Free Cash Flow: ", cash_flow)
print("Total Debt: ", total_debt)
print("Cash and ST Investments: ", cash_and_ST_investments)

print("EPS Growth 5Y: ", EPS_growth_5Y)
print("EPS Growth 6Y to 10Y: ", EPS_growth_6Y_to_10Y)
print("EPS Growth 11Y to 20Y: ", EPS_growth_11Y_to_20Y)

print("Discount Rate: ", discount_rate)
print("Shares Outstanding: ", shares_outstanding)

def calculate_intrinsic_value(cash_flow, total_debt, cash_and_ST_investments, 
                                  EPS_growth_5Y, EPS_growth_6Y_to_10Y, EPS_growth_11Y_to_20Y,
                                  shares_outstanding, discount_rate):   
    
    # Convert all percentages to decmials
    EPS_growth_5Y_d = EPS_growth_5Y/100
    EPS_growth_6Y_to_10Y_d = EPS_growth_6Y_to_10Y/100
    EPS_growth_11Y_to_20Y_d = EPS_growth_11Y_to_20Y/100
    discount_rate_d = discount_rate/100
    print("\nDiscounted Cash Flows:")
    
    # Projecting cash flows from year 1 to year 20
    cash_flow_list = []
    # Years 1 to 5
    for year in range(1, 6):
        cash_flow*=(1 + EPS_growth_5Y_d)
        cash_flow_discounted = cash_flow/((1 + discount_rate_d)**year)
        cash_flow_list.append(cash_flow_discounted)
        print("Year " + str(year) + ": $" + str(cash_flow_discounted)) ## Print out the projected discounted cash flows

    # Years 6 to 10        
    for year in range(6, 11):
        cash_flow*=(1 + EPS_growth_6Y_to_10Y_d)
        cash_flow_discounted = cash_flow/((1 + discount_rate_d)**year)
        cash_flow_list.append(cash_flow_discounted)
        print("Year " + str(year) + ": $" + str(cash_flow_discounted)) ## Print out the projected discounted cash flows

    # Years 11 to 20
    for year in range(11, 21):
        cash_flow*=(1 + EPS_growth_11Y_to_20Y_d)
        cash_flow_discounted = cash_flow/((1 + discount_rate_d)**year)
        cash_flow_list.append(cash_flow_discounted)
        print("Year " + str(year) + ": $" + str(cash_flow_discounted)) ## Print out the projected discounted cash flows
    
    intrinsic_value = (sum(cash_flow_list) - total_debt + cash_and_ST_investments)/shares_outstanding

    return intrinsic_value

intrinsic_value = calculate_intrinsic_value(cash_flow, total_debt, cash_and_ST_investments, 
                                  EPS_growth_5Y, EPS_growth_6Y_to_10Y, EPS_growth_11Y_to_20Y,
                                  shares_outstanding, discount_rate)    

print("\nIntrinsic Value: ", intrinsic_value)
current_price = finviz_data['Price']
print("Current Price: ", current_price)
print("Margin of Safety: ", (1-current_price/intrinsic_value)*100)