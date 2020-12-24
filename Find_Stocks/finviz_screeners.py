import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def long_term_buys_screener():
    try:
        url = ("https://finviz.com/screener.ashx?v=151&f=an_recom_holdbetter,cap_midover,fa_epsyoy1_o20,fa_salesqoq_o20,geo_usa,ind_stocksonly,sh_avgvol_o500,sh_insttrans_pos,sh_price_o10,ta_highlow52w_a30h,ta_perf_52w50o,ta_perf2_13wup,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa,targetprice_above&ft=4&o=change&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = soup(webpage, "html.parser")
        
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nLong Term Buys Screener: ')
print(long_term_buys_screener())

def intraday_buys_screener():
    try:
        url = ("https://finviz.com/screener.ashx?v=151&f=cap_midover,fa_epsyoy1_o20,fa_salesqoq_o20,geo_usa,ind_stocksonly,ipodate_prev3yrs,sh_avgvol_o500,sh_price_o15,ta_changeopen_u,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=change&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = soup(webpage, "html.parser")
        
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nIntraday Buys Screener Output: ')
print(intraday_buys_screener())

def long_term_shorts_screener():
    try:
        url = ("https://finviz.com/screener.ashx?v=151&f=cap_smallover,geo_usa,ind_stocksonly,sh_avgvol_o300,sh_price_o5,ta_sma20_pb,ta_sma200_pa100,targetprice_below&ft=4&o=-change&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = soup(webpage, "html.parser")
        
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nLong Term Short Screener Output: ')
print(long_term_shorts_screener())

def intraday_shorts_screener():
    try:
        url = ("https://finviz.com/screener.ashx?v=151&f=cap_smallover,geo_usa,ind_stocksonly,sh_price_o4,ta_change_u10,ta_rsi_ob60,ta_sma200_pa100&ft=4&o=-change&ar=180&c=0,1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,65,66,67,68,69")
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = soup(webpage, "html.parser")
        
        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks = stocks.set_index('Ticker')
        return stocks
    except Exception as e:
        return e

print ('\nIntraday Short Screener Output: ')
print(intraday_shorts_screener())
