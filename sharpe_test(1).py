# ROLLING SHARPE RATIO
import pickle
import datetime
import requests
import bs4 as bs
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
import seaborn as sns

sns.set_style("whitegrid")

start_date = datetime.datetime(2018,12,30)
end_date = datetime.date.today()

# save_sp500_tickers()
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
tickers = [item.replace(".", "-") for item in tickers]


#np.savez("sharpe_ratios.npz", sharpe_ratios)
all_sharpe_ratios = np.load("sharpe_ratios.npz")
all_sharpe_ratios = all_sharpe_ratios['arr_0'] 
all_sharpe_ratios = all_sharpe_ratios.tolist()

# Create a dataframe with each company and their corressponding beta/alpha values
dataframe = pd.DataFrame(list(zip(tickers, all_sharpe_ratios)), columns =['Company', 'Sharpe_Ratio']) 

pd.set_option('display.max_rows', None)
# Sorting the dataframe from highest beta values to lowest
sort_by_sharpe = dataframe.sort_values('Sharpe_Ratio', ascending = True)
print(sort_by_sharpe)