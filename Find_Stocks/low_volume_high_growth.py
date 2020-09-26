import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=cap_microover,geo_usa,sh_price_o3,sh_relvol_o2,ta_change_u5&ft=4&o=-change&c=0,1,2,3,4,6,7,26,28,42,43,44,45,46,47,49,52,53,54,57,58,59,60,63,64,65,66,67,69")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def find_top_stocks():
    try:
        data = pd.read_html(str(html))[8] 
        data.columns = data.iloc[0]
        data = data.drop(0)
        data = data.drop(columns=['No.'])
        data = data.set_index('Ticker')
        return data
    except Exception as e:
        return e

print ('\nLow Volume, High Growth Stocks: ')
print(find_top_stocks())
print ('-'*50)

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=cap_microover,geo_usa,sh_price_o3,sh_relvol_o2,ta_change_d5&ft=4&o=change&c=0,1,2,3,4,6,7,26,28,42,43,44,45,46,47,49,52,53,54,57,58,59,60,63,64,65,66,67,69")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def find_low_stocks():
    try:
        data = pd.read_html(str(html))[8] 
        data.columns = data.iloc[0]
        data = data.drop(0)
        data = data.drop(columns=['No.'])
        data = data.set_index('Ticker')
        return data
    except Exception as e:
        return e

print ('\nLow Volume, High Growth Stocks: ')
print(find_low_stocks())