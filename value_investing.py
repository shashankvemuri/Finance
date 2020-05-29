# Import The Libraries

# For data manipulation
import pandas as pd

# To extract fundamental data
from bs4 import BeautifulSoup as bs
import requests
import pickle

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

'''            try:
                df.loc[symbol, m] = fundamental_metric(soup, m)
            except Exception as e:
                print(symbol, 'not found')
                print(e)
                break
'''


# Define The Method To Extract Fundamental Data
def get_fundamental_data(df):
    for symbol in df.index:

        url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
        soup = bs(requests.get(url).content, features='html5lib')
        for m in df.columns:
            df.loc[symbol, m] = fundamental_metric(soup, m)
    return df


def fundamental_metric(soup, metric):
    return soup.find(text=metric).find_next(class_='snapshot-td2-cp').text

# Define A List Of Stocks And The Fundamental Metrics
# save_sp500_tickers()
def save_spx_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soups = bs(resp.text, 'lxml')
    tables = soups.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in tables.findAll('tr')[1:]:
        ticker = row.find_all('td') [0].text.strip()
        tickers.append(ticker)
        
    with open('spxTickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)       
    return tickers
        
tickers = save_spx_tickers()
tickers = [item.replace(".", "-") for item in tickers]

stock_list = tickers 

metric = ['P/B',
          'P/E',
          'Forward P/E',
          'PEG',
          'Debt/Eq',
          'EPS (ttm)',
          'Dividend %',
          'ROE',
          'ROI',
          'EPS Q/Q',
          'Insider Own'
          ]

df = pd.DataFrame(index=stock_list, columns=metric)
df = get_fundamental_data(df)
print("All stocks with fundamental data")
print(df.head())
df.to_csv('/Users/shashank/Downloads/fundamental_data.csv')