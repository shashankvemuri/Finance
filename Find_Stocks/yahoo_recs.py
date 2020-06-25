import requests
import pandas as pd 
from yahoo_fin import stock_info as si 
from pandas_datareader import DataReader
import numpy as np
import datetime
import time
import bs4 as bs
import pickle

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

def save_spx_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.find_all('td') [0].text.strip()
        tickers.append(ticker)
        
    with open('spxTickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)       
    return tickers
        
tickers = save_spx_tickers()

# Make the ticker symbols readable by Yahoo Finance
tickers = [item.replace(".", "-") for item in tickers]

recommendations = []

for ticker in tickers:
    lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'
              
    url =  lhs_url + ticker + rhs_url
    r = requests.get(url)
    if not r.ok:
        recommendation = 6
    try:
        result = r.json()['quoteSummary']['result'][0]
        recommendation =result['financialData']['recommendationMean']['fmt']
    except:
        recommendation = 6
    
    recommendations.append(recommendation)
    time.sleep(1.5)
    
    #print("--------------------------------------------")
    print ("{} has an average recommendation of: ".format(ticker), recommendation)
    

df = pd.read_csv('/Users/shashank/Documents/GitHub/Code/recommendation-values/recommendation-values.csv')
df['{}'.format(today)] = recommendations
df = df.set_index('Company')
df.to_csv('/Users/shashank/Documents/GitHub/Code/recommendation-values/recommendation-values.csv')

#dataframe = pd.read_csv('recommendations.csv')
#print (dataframe)