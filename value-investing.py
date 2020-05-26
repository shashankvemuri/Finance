# Import The Libraries

# For data manipulation
import pandas as pd

# To extract fundamental data
from bs4 import BeautifulSoup as bs
import requests
import pickle

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Define The Method To Extract Fundamental Data

'''
def get_fundamental_data(df):
    for symbol in df.index:

        url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
        soup = bs(requests.get(url).content, features='html5lib')
        for m in df.columns:
            try:
                df.loc[symbol, m] = fundamental_metric(soup, m)
            except Exception as e:
                print(symbol, 'not found')
                print(e)
                break
    return df


def fundamental_metric(soup, metric):
    return soup.find(text=metric).find_next(class_='snapshot-td2').text


# Define A List Of Stocks And The Fundamental Metrics
# save_sp500_tickers()
def save_spx_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs(resp.text, 'lxml')
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

# 1. Businesses which are quoted at low valuations
#P/E < 20
#P/B < 3

try:
    df = df[(df['P/E'].astype(float) < 20) & (df['P/B'].astype(float) < 3)]
    df.to_csv('/Users/shashank/Downloads/low_valuations.csv')
except:
    pass

# 2. Businesses which have demonstrated earning power
# EPS Q/Q > 10%
try:
    df['EPS Q/Q'] = df['EPS Q/Q'].map(lambda x: x[:-1])
    df = df[df['EPS Q/Q'].astype(float) > 10]
    df.to_csv('/Users/shashank/Downloads/earning_power.csv')
except:
    pass

# 3. Businesses earning good returns on equity while employing little or no debt
#Debt/Eq < 1
# ROE > 10%

try:
    df['ROE'] = df['ROE'].map(lambda x: x[:-1])
    df = df[(df['Debt/Eq'].astype(float) < 1) & (df['ROE'].astype(float) > 10)]
    df.to_csv('/Users/shashank/Downloads/returns_on_equity.csv')
except:
    pass

# 4. Management having substantial ownership in the business
# Insider own > 30%

try:
    df['Insider Own'] = df['Insider Own'].map(lambda x: x[:-1])
    df = df[df['Insider Own'].astype(float) > 30]
    df.to_csv('/Users/shashank/Downloads/insider_own.csv')
except:
    pass

print ('\n')
print("Stocks after screening")
print(df.head())
df.to_csv('/Users/shashank/Downloads/after_screening.csv')
'''


pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)

df = pd.read_csv('fundamental_data.csv')
df.rename(columns={'Unnamed: 0': 'Companies'}, inplace=True)
df = df.set_index('Companies')

#print (df.tail(50))

sort_by_ROI= df.sort_values('P/E', ascending = False)
print(sort_by_ROI)