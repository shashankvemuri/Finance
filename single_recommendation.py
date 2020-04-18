import datetime
import requests
import pandas as pd 
from yahoo_fin import stock_info as si 
from pandas_datareader import DataReader
import numpy as np
import FundamentalAnalysis as fa
from pandas_datareader import data as pdr
import os
from pandas import ExcelWriter

ticker = "AAL"

lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
          'modules=upgradeDowngradeHistory,recommendationTrend,' \
          'financialData,earningsHistory,earningsTrend,industryTrend&' \
          'corsDomain=finance.yahoo.com'
          
url =  lhs_url + ticker + rhs_url
r = requests.get(url)
if not r.ok:
    recommendation = 0
try:
    result = r.json()['quoteSummary']['result'][0]
    recommendation =result['financialData']['recommendationMean']['fmt']
except:
    recommendation = 0
    
print (recommendation)