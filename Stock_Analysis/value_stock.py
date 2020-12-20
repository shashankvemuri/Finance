# Code from https://medium.com/datadriveninvestor/use-python-to-value-a-stock-automatically-3b520422ab6 by Bohmian

# Importing required modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import time
from config import financial_model_prep
pd.set_option('display.max_columns', None)

# Settings to produce nice plots in a Jupyter notebook
plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = [15, 10]
import seaborn as sns

# To extract and parse fundamental data from finviz website
import requests
from bs4 import BeautifulSoup as bs
import warnings
warnings.filterwarnings('ignore')

# For parsing financial statements data from financialmodelingprep api
from urllib.request import urlopen
import json

def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# inputs
base_url = "https://financialmodelingprep.com/api/v3/"
tickers = ['AAL', 
'ACGL', 
'AEM', 
'ALSN', 
'AMX', 
'APPS', 
'BKNG', 
'BLD', 
'BX', 
'CMG', 
'CSL', 
'DIOD', 
'DOMO', 
'DOYU', 
'EDU', 
'EHC', 
'ENPH', 
'ESGR', 
'EXPI', 
'FUN', 
'FUTU', 
'HAE', 
'HSIC', 
'IBN', 
'IBP', 
'ISRG', 
'JD', 
'KKR', 
'KNSL', 
'LAMR', 
'LNG', 
'LULU', 
'MA', 
'MGM', 
'MRVL', 
'NCR', 
'NFLX', 
'NIO', 
'NIU', 
'OLED', 
'PAGS', 
'PCRX', 
'RCM', 
'REGI', 
'SBSW', 
'SGMS', 
'SPWR', 
'SQ', 
'SYF', 
'WKHS', 
'WYND', 
'XP', 
'XRX', 
'YY']
apiKey = financial_model_prep()

cash_flows = []
total_debts = []
cash_and_ST_investments_list = []
betas = []
discount_rates = []
EPS_growth_5Ys = []
EPS_growth_6Y_to_10Ys = []
EPS_growth_11Y_to_20Ys = []
shares_outstandings = []
intrinsic_values = []
current_prices = []
margins_safety = []
valid_tickers = []

for ticker in tickers:
    try:
        q_cash_flow_statement = pd.DataFrame(get_jsonparsed_data(base_url+'cash-flow-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
        q_cash_flow_statement = q_cash_flow_statement.set_index('date').iloc[:4] # extract for last 4 quarters
        q_cash_flow_statement = q_cash_flow_statement.apply(pd.to_numeric, errors='coerce')
        
        cash_flow_statement = pd.DataFrame(get_jsonparsed_data(base_url+'cash-flow-statement/' + ticker + '?apikey=' + apiKey))
        cash_flow_statement = cash_flow_statement.set_index('date')
        cash_flow_statement = cash_flow_statement.apply(pd.to_numeric, errors='coerce')
        
        ttm_cash_flow_statement = q_cash_flow_statement.sum() # sum up last 4 quarters to get TTM cash flow
        cash_flow_statement = cash_flow_statement[::-1].append(ttm_cash_flow_statement.rename('TTM')).drop(['netIncome'], axis=1)
        final_cash_flow_statement = cash_flow_statement[::-1] # reverse list to show most recent ones first
        
        # final_cash_flow_statement[['freeCashFlow']].iloc[::-1].iloc[-15:].plot(kind='bar', title=ticker + ' Cash Flows')
        # plt.show()
        
        q_balance_statement = pd.DataFrame(get_jsonparsed_data(base_url+'balance-sheet-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
        q_balance_statement = q_balance_statement.set_index('date')
        q_balance_statement = q_balance_statement.apply(pd.to_numeric, errors='coerce')
        
        cash_flow = final_cash_flow_statement.iloc[0]['freeCashFlow']
        total_debt = q_balance_statement.iloc[0]['totalDebt'] 
        cash_and_ST_investments = q_balance_statement.iloc[0]['cashAndShortTermInvestments']
        
        # print("Free Cash Flow: ", cash_flow)
        # print("Total Debt: ", total_debt)
        # print("Cash and ST Investments: ", cash_and_ST_investments)
        
        # List of data we want to extract from Finviz Table
        metric = ['Price', 'EPS next 5Y', 'Beta', 'Shs Outstand']
        
        def fundamental_metric(soup, metric):
            # the table which stores the data in Finviz has html table attribute class of 'snapshot-td2'
            return soup.find(text = metric).find_next(class_='snapshot-td2').text
           
        def get_finviz_data(ticker):
            try:
                url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
                soup = bs(requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}).content)
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
        # print('\nFinViz Data:\n' + str(finviz_data))
        
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
        
        # print("\nDiscount Rate: ", discount_rate)
        
        EPS_growth_5Y = finviz_data['EPS next 5Y']
        EPS_growth_6Y_to_10Y = EPS_growth_5Y/2  # Half the previous growth rate, conservative estimate
        EPS_growth_11Y_to_20Y  = np.minimum(EPS_growth_6Y_to_10Y, 4)  # Slightly higher than long term inflation rate, conservative estimate
        
        shares_outstanding = round(finviz_data['Shs Outstand'])
        
        # print("Free Cash Flow: ", cash_flow)
        # print("Total Debt: ", total_debt)
        # print("Cash and ST Investments: ", cash_and_ST_investments)
        
        # print("EPS Growth 5Y: ", EPS_growth_5Y)
        # print("EPS Growth 6Y to 10Y: ", EPS_growth_6Y_to_10Y)
        # print("EPS Growth 11Y to 20Y: ", EPS_growth_11Y_to_20Y)
        
        # print("Discount Rate: ", discount_rate)
        
        # print("Shares Outstanding: ", shares_outstanding)
        
        def calculate_intrinsic_value(cash_flow, total_debt, cash_and_ST_investments, 
                                          EPS_growth_5Y, EPS_growth_6Y_to_10Y, EPS_growth_11Y_to_20Y,
                                          shares_outstanding, discount_rate):   
            
            # Convert all percentages to decmials
            EPS_growth_5Y_d = EPS_growth_5Y/100
            EPS_growth_6Y_to_10Y_d = EPS_growth_6Y_to_10Y/100
            EPS_growth_11Y_to_20Y_d = EPS_growth_11Y_to_20Y/100
            discount_rate_d = discount_rate/100
            # print("\nDiscounted Cash Flows")
            
            # Lists of projected cash flows from year 1 to year 20
            cash_flow_list = []
            cash_flow_discounted_list = []
            year_list = []
            
            
            # Years 1 to 5
            for year in range(1, 6):
                year_list.append(year)
                cash_flow*=(1 + EPS_growth_5Y_d)        
                cash_flow_list.append(cash_flow)
                cash_flow_discounted = cash_flow/((1 + discount_rate_d)**year)
                cash_flow_discounted_list.append(cash_flow_discounted)
                # print("Year " + str(year) + ": $" + str(cash_flow_discounted)) ## Print out the projected discounted cash flows
            
            # Years 6 to 10
            for year in range(6, 11):
                year_list.append(year)
                cash_flow*=(1 + EPS_growth_6Y_to_10Y_d)
                cash_flow_list.append(cash_flow)
                cash_flow_discounted = cash_flow/((1 + discount_rate_d)**year)
                cash_flow_discounted_list.append(cash_flow_discounted)
                # print("Year " + str(year) + ": $" + str(cash_flow_discounted)) ## Print out the projected discounted cash flows
            
            # Years 11 to 20
            for year in range(11, 21):
                year_list.append(year)
                cash_flow*=(1 + EPS_growth_11Y_to_20Y_d)
                cash_flow_list.append(cash_flow)
                cash_flow_discounted = cash_flow/((1 + discount_rate_d)**year)
                cash_flow_discounted_list.append(cash_flow_discounted)
                # print("Year " + str(year) + ": $" + str(cash_flow_discounted)) ## Print out the projected discounted cash flows
            
            intrinsic_value = (sum(cash_flow_discounted_list) - total_debt + cash_and_ST_investments)/shares_outstanding
            df = pd.DataFrame.from_dict({'Year': year_list, 'Cash Flow': cash_flow_list, 'Discounted Cash Flow': cash_flow_discounted_list})
            df.index = df.Year
            # df.plot(kind='bar', title = 'Projected Cash Flows of ' + ticker)
            # plt.show()
        
            return intrinsic_value
        
        
        intrinsic_value = round(calculate_intrinsic_value(cash_flow, total_debt, cash_and_ST_investments, 
                                          EPS_growth_5Y, EPS_growth_6Y_to_10Y, EPS_growth_11Y_to_20Y,
                                          shares_outstanding, discount_rate), 2)    
        
        # print("\nIntrinsic Value: ", intrinsic_value)
        current_price = finviz_data['Price']
        # print("Current Price: ", current_price)
        change = round(((intrinsic_value-current_price)/current_price)*100, 2)
        # print("Margin of Safety: ", margin_safety)
        
        cash_flows.append(cash_flow)
        total_debts.append(total_debt)
        cash_and_ST_investments_list.append(cash_and_ST_investments)
        betas.append(Beta)
        discount_rates.append(discount_rate)
        EPS_growth_5Ys.append(EPS_growth_5Y)
        EPS_growth_6Y_to_10Ys.append(EPS_growth_6Y_to_10Y)
        EPS_growth_11Y_to_20Ys.append(EPS_growth_11Y_to_20Y)
        shares_outstandings.append(shares_outstanding)
        intrinsic_values.append(intrinsic_value)
        current_prices.append(current_price)
        margins_safety.append(change)
        valid_tickers.append(ticker)
    except:
        pass
    
df = pd.DataFrame(np.column_stack([valid_tickers, cash_flows, total_debts, cash_and_ST_investments_list, betas, discount_rates, EPS_growth_5Ys, EPS_growth_6Y_to_10Ys, EPS_growth_11Y_to_20Ys, shares_outstandings, intrinsic_values, current_prices, margins_safety]), 
                               columns=['Ticker', 'Cash Flow', 'Total Debt', 'Cash and ST investment', 'Beta', 'Discount Rate', 'EPS Growth 5 Y', 'EPS Growth 6-10 Y', 'EPS Growth 11-20 Y', 'Shares Outstanding', 'Intrinsic Value', 'Current Price', 'Margin Safety']).set_index('Ticker')
df = df.sort_values(['Margin Safety'], ascending=True)
df.to_csv(f'/Users/shashank/Downloads/{time.time()}.csv')
print (df)
