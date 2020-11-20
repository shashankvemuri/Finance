import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def growth_screener():
    try:
        frames = []
        for i in range(1, 105, 20):
            url = (f"https://finviz.com/screener.ashx?v=111&f=fa_epsyoy_o20,fa_epsyoy1_o25,fa_roe_o10,sh_price_o5,ta_sma200_pa&ft=4&r=0{i}")
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            html = soup(webpage, "html.parser")
            
            stocks = pd.read_html(str(html))[-2]
            stocks.columns = stocks.iloc[0]
            stocks = stocks[1:]
            stocks = stocks.set_index('Ticker')
            frames.append(stocks)
        df = pd.concat(frames)
        df = df.drop_duplicates()
        df = df.drop(columns = ['No.'])
        return df
    except Exception as e:
        return e

print ('\nGrowth Stocks Screener: ')
print(growth_screener())

for ticker in growth_screener().index:
    print (ticker+', ')