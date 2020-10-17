import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=cap_midover,fa_epsyoy1_o20,fa_salesqoq_o20,geo_usa,ind_stocksonly,sh_avgvol_o500,sh_insttrans_pos,sh_price_o10,ta_highlow52w_a30h,ta_perf_52w50o,ta_perf2_13wup,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-volume&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def own_screener():
    try:
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nLong Term Buys Screener Output: ')
print(own_screener())

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=cap_midover,fa_epsyoy1_o20,fa_salesqoq_o20,geo_usa,ind_stocksonly,ipodate_prev3yrs,sh_avgvol_o500,sh_price_o15,ta_changeopen_u,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-volume&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def alpha_screener():
    try:
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nIntraday Buys Screener Output: ')
print(alpha_screener())

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=cap_smallover,geo_usa,ind_stocksonly,sh_avgvol_o300,sh_insidertrans_neg,sh_price_o5,ta_sma20_pb,ta_sma200_pa100,targetprice_below&ft=4&o=-volume&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def long_short_screener():
    try:
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nLong Term Short Screener Output: ')
print(long_short_screener())

# Set up scraper
url = ("https://finviz.com/screener.ashx?v=151&f=cap_smallover,geo_usa,ind_stocksonly,sh_avgvol_o300,sh_insidertrans_neg,sh_insttrans_neg,sh_price_o7,ta_changeopen_d,ta_rsi_ob60,ta_sma200_pa100,targetprice_below&ft=4&o=-volume&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def int_short_screener():
    try:
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nIntraday Short Screener Output: ')
print(int_short_screener())