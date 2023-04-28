# Import dependencies
import requests
import pandas as pd 
from yahoo_fin import stock_info as si 
from pandas_datareader import DataReader
import numpy as np
import datetime
import time
import bs4 as bs
import pickle

# Define today's date
today = datetime.date.today()

def save_spx_tickers():
    """
    Scrape S&P 500 tickers from Wikipedia and save them in a pickle file
    Returns:
        tickers (list): a list of S&P 500 tickers
    """
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.find_all('td')[0].text.strip()
        tickers.append(ticker)
        
    with open('spxTickers.pickle', 'wb') as f:
        pickle.dump(tickers, f)       
    return tickers
        
tickers = save_spx_tickers()

# Replace dots with hyphens in ticker symbols to make them readable by Yahoo Finance
tickers = [item.replace(".", "-") for item in tickers]

recommendations = []

for ticker in tickers:
    lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'
              
    url = lhs_url + ticker + rhs_url
    r = requests.get(url)
    if not r.ok:
        recommendation = 6 # Default recommendation if request fails
    try:
        result = r.json()['quoteSummary']['result'][0]
        recommendation = result['financialData']['recommendationMean']['fmt']
    except:
        recommendation = 6 # Default recommendation if parsing fails
    
    recommendations.append(recommendation)
    time.sleep(1.5) # Sleep for 1.5 seconds before sending another request
    
    # Print the recommendation for each ticker
    print("{} has an average recommendation of: {}".format(ticker, recommendation))
    
# Load the existing recommendation file and update it with today's recommendations
df = pd.read_csv('recommendation-values.csv', index_col='Company')
df[today] = recommendations
df.to_csv('recommendation-values.csv')
print(df)