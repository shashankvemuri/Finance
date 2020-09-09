import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=an_recom_buybetter,fa_pe_profitable,geo_usa,idx_sp500,ind_stocksonly,sh_avgvol_o1000,sh_insttrans_pos,sh_price_o2,ta_rsi_nob60,ta_sma20_sa50,ta_sma50_sa200,targetprice_above&ft=4&o=relativevolume&ar=180")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def finviz_screener():
    try:
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = ['No.', 'Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Market Cap', 'P/E', 'Price', 'Change', 'Volume']
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nScreener Output: ')
print(finviz_screener())