import requests
import numpy as np
import pandas as pd

company = 'GOOG'
demo = 'your api key'
IS = requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?apikey={demo}').json()
count = 0
#get revenue growth to estimate future sales
revenue_g = []
for item in IS:
  if count < 4:
    #print(item)
    revenue_g.append(item['revenue'])
    count = count + 1

revenue_g = (revenue_g[0] - revenue_g[1]) /revenue_g[0] 
#revenue_g = 0.05
print(revenue_g)
#Get net income
net_income = IS[0]['netIncome']

BS = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?apikey={demo}').json()

#get income statement as % of revenue for future predictions and forecast 5 next IS years
income_statement = pd.DataFrame.from_dict(IS[0],orient='index')
income_statement = income_statement[5:26]
income_statement.columns = ['current_year']
income_statement['as_%_of_revenue'] = income_statement / income_statement.iloc[0]

#forecasting 5 next years income statement
income_statement['next_year'] =  (income_statement['current_year']['revenue'] * (1+revenue_g)) * income_statement['as_%_of_revenue'] 
income_statement['next_2_year'] =  (income_statement['next_year']['revenue'] * (1+revenue_g)) * income_statement['as_%_of_revenue'] 
income_statement['next_3_year'] =  (income_statement['next_2_year']['revenue'] * (1+revenue_g)) * income_statement['as_%_of_revenue'] 
income_statement['next_4_year'] =  (income_statement['next_3_year']['revenue'] * (1+revenue_g)) * income_statement['as_%_of_revenue'] 
income_statement['next_5_year'] =  (income_statement['next_4_year']['revenue'] * (1+revenue_g)) * income_statement['as_%_of_revenue'] 

#Get Balance sheet as a percentage of revenue
balance_sheet = pd.DataFrame.from_dict(BS[0],orient='index')
balance_sheet = balance_sheet[5:-2]
balance_sheet.columns = ['current_year']
balance_sheet['as_%_of_revenue'] = balance_sheet / income_statement['current_year'].iloc[0]

#forecasting the next 5 years Balance Sheet.
balance_sheet['next_year'] =  income_statement['next_year'] ['revenue'] * balance_sheet['as_%_of_revenue']
balance_sheet['next_2_year'] =  income_statement['next_2_year'] ['revenue'] * balance_sheet['as_%_of_revenue']
balance_sheet['next_3_year'] =  income_statement['next_3_year']['revenue'] * balance_sheet['as_%_of_revenue'] 
balance_sheet['next_4_year'] =  income_statement['next_4_year']['revenue']  * balance_sheet['as_%_of_revenue'] 
balance_sheet['next_5_year'] =  income_statement['next_5_year']['revenue'] * balance_sheet['as_%_of_revenue']

CF_forecast = {}
CF_forecast['next_year'] = {}
CF_forecast['next_year']['netIncome'] = income_statement['next_year']['netIncome']
CF_forecast['next_year']['inc_depreciation'] = income_statement['next_year']['depreciationAndAmortization'] - income_statement['current_year']['depreciationAndAmortization']
CF_forecast['next_year']['inc_receivables'] = balance_sheet['next_year']['netReceivables'] - balance_sheet['current_year']['netReceivables']
CF_forecast['next_year']['inc_inventory'] = balance_sheet['next_year']['inventory'] - balance_sheet['current_year']['inventory']
CF_forecast['next_year']['inc_payables'] = balance_sheet['next_year']['accountPayables'] - balance_sheet['current_year']['accountPayables']
CF_forecast['next_year']['CF_operations'] = CF_forecast['next_year']['netIncome'] + CF_forecast['next_year']['inc_depreciation'] + (CF_forecast['next_year']['inc_receivables'] * -1) + (CF_forecast['next_year']['inc_inventory'] *-1) + CF_forecast['next_year']['inc_payables']
CF_forecast['next_year']['CAPEX'] = balance_sheet['next_year']['propertyPlantEquipmentNet'] - balance_sheet['current_year']['propertyPlantEquipmentNet'] + income_statement['next_year']['depreciationAndAmortization']

CF_forecast['next_year']['FCF'] = CF_forecast['next_year']['CAPEX'] + CF_forecast['next_year']['CF_operations']


CF_forecast['next_2_year'] = {}
CF_forecast['next_2_year']['netIncome'] = income_statement['next_2_year']['netIncome']

CF_forecast['next_2_year']['inc_depreciation'] = income_statement['next_2_year']['depreciationAndAmortization'] - income_statement['next_year']['depreciationAndAmortization']
CF_forecast['next_2_year']['inc_receivables'] = balance_sheet['next_2_year']['netReceivables'] - balance_sheet['next_year']['netReceivables']
CF_forecast['next_2_year']['inc_inventory'] = balance_sheet['next_2_year']['inventory'] - balance_sheet['next_year']['inventory']
CF_forecast['next_2_year']['inc_payables'] = balance_sheet['next_2_year']['accountPayables'] - balance_sheet['next_year']['accountPayables']
CF_forecast['next_2_year']['CF_operations'] = CF_forecast['next_2_year']['netIncome'] + CF_forecast['next_2_year']['inc_depreciation'] + (CF_forecast['next_2_year']['inc_receivables'] * -1) + (CF_forecast['next_2_year']['inc_inventory'] *-1) + CF_forecast['next_2_year']['inc_payables']
CF_forecast['next_2_year']['CAPEX'] = balance_sheet['next_2_year']['propertyPlantEquipmentNet'] - balance_sheet['next_year']['propertyPlantEquipmentNet'] + income_statement['next_2_year']['depreciationAndAmortization']
CF_forecast['next_2_year']['FCF'] = CF_forecast['next_2_year']['CAPEX'] + CF_forecast['next_2_year']['CF_operations']


CF_forecast['next_3_year'] = {}
CF_forecast['next_3_year']['netIncome'] = income_statement['next_3_year']['netIncome']

CF_forecast['next_3_year']['inc_depreciation'] = income_statement['next_3_year']['depreciationAndAmortization'] - income_statement['next_2_year']['depreciationAndAmortization']
CF_forecast['next_3_year']['inc_receivables'] = balance_sheet['next_3_year']['netReceivables'] - balance_sheet['next_2_year']['netReceivables']
CF_forecast['next_3_year']['inc_inventory'] = balance_sheet['next_3_year']['inventory'] - balance_sheet['next_2_year']['inventory']
CF_forecast['next_3_year']['inc_payables'] = balance_sheet['next_3_year']['accountPayables'] - balance_sheet['next_2_year']['accountPayables']
CF_forecast['next_3_year']['CF_operations'] = CF_forecast['next_3_year']['netIncome'] + CF_forecast['next_3_year']['inc_depreciation'] + (CF_forecast['next_3_year']['inc_receivables'] * -1) + (CF_forecast['next_3_year']['inc_inventory'] *-1) + CF_forecast['next_3_year']['inc_payables']
CF_forecast['next_3_year']['CAPEX'] = balance_sheet['next_3_year']['propertyPlantEquipmentNet'] - balance_sheet['next_2_year']['propertyPlantEquipmentNet'] + income_statement['next_3_year']['depreciationAndAmortization']
CF_forecast['next_3_year']['FCF'] = CF_forecast['next_3_year']['CAPEX'] + CF_forecast['next_3_year']['CF_operations']


CF_forecast['next_4_year'] = {}
CF_forecast['next_4_year']['netIncome'] = income_statement['next_4_year']['netIncome']

CF_forecast['next_4_year']['inc_depreciation'] = income_statement['next_4_year']['depreciationAndAmortization'] - income_statement['next_3_year']['depreciationAndAmortization']
CF_forecast['next_4_year']['inc_receivables'] = balance_sheet['next_4_year']['netReceivables'] - balance_sheet['next_3_year']['netReceivables']
CF_forecast['next_4_year']['inc_inventory'] = balance_sheet['next_4_year']['inventory'] - balance_sheet['next_3_year']['inventory']
CF_forecast['next_4_year']['inc_payables'] = balance_sheet['next_4_year']['accountPayables'] - balance_sheet['next_3_year']['accountPayables']
CF_forecast['next_4_year']['CF_operations'] = CF_forecast['next_4_year']['netIncome'] + CF_forecast['next_4_year']['inc_depreciation'] + (CF_forecast['next_4_year']['inc_receivables'] * -1) + (CF_forecast['next_4_year']['inc_inventory'] *-1) + CF_forecast['next_4_year']['inc_payables']
CF_forecast['next_4_year']['CAPEX'] = balance_sheet['next_4_year']['propertyPlantEquipmentNet'] - balance_sheet['next_3_year']['propertyPlantEquipmentNet'] + income_statement['next_4_year']['depreciationAndAmortization']
CF_forecast['next_4_year']['FCF'] = CF_forecast['next_4_year']['CAPEX'] + CF_forecast['next_4_year']['CF_operations']

CF_forecast['next_5_year'] = {}
CF_forecast['next_5_year']['netIncome'] = income_statement['next_5_year']['netIncome']

CF_forecast['next_5_year']['inc_depreciation'] = income_statement['next_5_year']['depreciationAndAmortization'] - income_statement['next_4_year']['depreciationAndAmortization']
CF_forecast['next_5_year']['inc_receivables'] = balance_sheet['next_5_year']['netReceivables'] - balance_sheet['next_4_year']['netReceivables']
CF_forecast['next_5_year']['inc_inventory'] = balance_sheet['next_5_year']['inventory'] - balance_sheet['next_4_year']['inventory']
CF_forecast['next_5_year']['inc_payables'] = balance_sheet['next_5_year']['accountPayables'] - balance_sheet['next_4_year']['accountPayables']
CF_forecast['next_5_year']['CF_operations'] = CF_forecast['next_5_year']['netIncome'] + CF_forecast['next_5_year']['inc_depreciation'] + (CF_forecast['next_5_year']['inc_receivables'] * -1) + (CF_forecast['next_5_year']['inc_inventory'] *-1) + CF_forecast['next_5_year']['inc_payables']
CF_forecast['next_5_year']['CAPEX'] = balance_sheet['next_5_year']['propertyPlantEquipmentNet'] - balance_sheet['next_4_year']['propertyPlantEquipmentNet'] + income_statement['next_5_year']['depreciationAndAmortization']
CF_forecast['next_5_year']['FCF'] = CF_forecast['next_5_year']['CAPEX'] + CF_forecast['next_5_year']['CF_operations']

#add the forecasted cash flows into a Pandas
CF_forec = pd.DataFrame.from_dict(CF_forecast,orient='columns')

#add below option to format the dataframe with thousand separators
pd.options.display.float_format = '{:,.0f}'.format

print(CF_forec)

import pandas_datareader.data as web
import datetime
import requests


#demo = 'your api key'
#Interest coverage ratio = EBIT / interest expenses

def interest_coveraga_and_RF(company):
  IS= requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?apikey={demo}').json()
  EBIT= IS[0]['ebitda'] - IS[0]['depreciationAndAmortization'] 
  interest_expense = IS[0]['interestExpense']
  interest_coverage_ratio = EBIT / interest_expense

    #RF
  start = datetime.datetime(2019, 7, 10)
        
  end= datetime.datetime.today().strftime('%Y-%m-%d')
  #end = datetime.datetime(2020, 7, 10)

  Treasury = web.DataReader(['TB1YR'], 'fred', start, end)
  RF = float(Treasury.iloc[-1])
  RF = RF/100
  return [RF,interest_coverage_ratio]
  
#Cost of debt
def cost_of_debt(company, RF,interest_coverage_ratio):
  if interest_coverage_ratio > 8.5:
    #Rating is AAA
    credit_spread = 0.0063
  if (interest_coverage_ratio > 6.5) & (interest_coverage_ratio <= 8.5):
    #Rating is AA
    credit_spread = 0.0078
  if (interest_coverage_ratio > 5.5) & (interest_coverage_ratio <=  6.5):
    #Rating is A+
    credit_spread = 0.0098
  if (interest_coverage_ratio > 4.25) & (interest_coverage_ratio <=  5.49):
    #Rating is A
    credit_spread = 0.0108
  if (interest_coverage_ratio > 3) & (interest_coverage_ratio <=  4.25):
    #Rating is A-
    credit_spread = 0.0122
  if (interest_coverage_ratio > 2.5) & (interest_coverage_ratio <=  3):
    #Rating is BBB
    credit_spread = 0.0156
  if (interest_coverage_ratio > 2.25) & (interest_coverage_ratio <=  2.5):
    #Rating is BB+
    credit_spread = 0.02
  if (interest_coverage_ratio > 2) & (interest_coverage_ratio <=  2.25):
    #Rating is BB
    credit_spread = 0.0240
  if (interest_coverage_ratio > 1.75) & (interest_coverage_ratio <=  2):
    #Rating is B+
    credit_spread = 0.0351
  if (interest_coverage_ratio > 1.5) & (interest_coverage_ratio <=  1.75):
    #Rating is B
    credit_spread = 0.0421
  if (interest_coverage_ratio > 1.25) & (interest_coverage_ratio <=  1.5):
    #Rating is B-
    credit_spread = 0.0515
  if (interest_coverage_ratio > 0.8) & (interest_coverage_ratio <=  1.25):
    #Rating is CCC
    credit_spread = 0.0820
  if (interest_coverage_ratio > 0.65) & (interest_coverage_ratio <=  0.8):
    #Rating is CC
    credit_spread = 0.0864
  if (interest_coverage_ratio > 0.2) & (interest_coverage_ratio <=  0.65):
    #Rating is C
    credit_spread = 0.1134
  if interest_coverage_ratio <=  0.2:
    #Rating is D
    credit_spread = 0.1512
  
  cost_of_debt = RF + credit_spread
  return cost_of_debt


def costofequity(company):


  #RF
  start = datetime.datetime(2019, 7, 10)
  end= datetime.datetime.today().strftime('%Y-%m-%d')
  #end = datetime.datetime(2020, 7, 10)

  Treasury = web.DataReader(['TB1YR'], 'fred', start, end)
  RF = float(Treasury.iloc[-1])
  RF = RF/100

#Beta

  beta = requests.get(f'https://financialmodelingprep.com/api/v3/company/profile/{company}?apikey={demo}')
  beta = beta.json()
  beta = float(beta['profile']['beta'])


  #Market Return
  start = datetime.datetime(2019, 7, 10)
  end= datetime.datetime.today().strftime('%Y-%m-%d')

  SP500 = web.DataReader(['sp500'], 'fred', start, end)
      #Drop all Not a number values using drop method.
  SP500.dropna(inplace = True)

  SP500yearlyreturn = (SP500['sp500'].iloc[-1]/ SP500['sp500'].iloc[-252])-1
    
  cost_of_equity = RF+(beta*(SP500yearlyreturn - RF))
  return cost_of_equity

#effective tax rate and capital structure
def wacc(company):
  FR = requests.get(f'https://financialmodelingprep.com/api/v3/ratios/{company}?apikey={demo}').json()

  ETR = FR[0]['effectiveTaxRate']

# 
  BS = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?period=quarter&apikey={demo}').json()



  Debt_to = BS[0]['totalDebt'] / (BS[0]['totalDebt'] + BS[0]['totalStockholdersEquity'])
  equity_to = BS[0]['totalStockholdersEquity'] / (BS[0]['totalDebt'] + BS[0]['totalStockholdersEquity'])

  WACC = (kd*(1-ETR)*Debt_to) + (ke*equity_to)
  return WACC

RF_and_IntCov = interest_coveraga_and_RF(company)
RF = RF_and_IntCov[0]
interest_coverage_ratio = RF_and_IntCov[1]
ke = costofequity(company)
kd = cost_of_debt(company,RF,interest_coverage_ratio)
wacc_company = wacc(company)
print('wacc of ' + company + ' is ' + str((wacc_company*100))+'%')


#FCF List of CFs for each year
FCF_List = CF_forec.iloc[-1].values.tolist()
npv = np.npv(wacc_company,FCF_List)

#Terminal value
LTGrowth = 0.02

Terminal_value = (CF_forecast['next_5_year']['FCF'] * (1+ LTGrowth)) /(wacc_company  - LTGrowth)

Terminal_value_Discounted = Terminal_value/(1+wacc_company)**4
Terminal_value_Discounted

target_equity_value = Terminal_value_Discounted + npv
debt = balance_sheet['current_year']['totalDebt']
target_value = target_equity_value - debt
numbre_of_shares = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-values/{company}?apikey={demo}').json()
numbre_of_shares = numbre_of_shares[0]['numberOfShares']

target_price_per_share = target_value/numbre_of_shares
target_price_per_share
print(company + ' forecasted price per stock is ' + str(target_price_per_share) )
print('the forecast is based on the following assumptions: '+ 'revenue growth: ' + str(revenue_g) + ' Cost of Capital: ' + str(wacc_company) )
print('perpetuity growth: ' + str(LTGrowth))