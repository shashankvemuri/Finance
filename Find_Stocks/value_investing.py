import pandas as pd
from selenium import webdriver
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options
from yahoo_fin import stock_info as si
import datetime 

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome('../chromedriver', options=options)

def finviz_parser(stock_list, metric):
    def get_fundamental_data(df):
        for symbol in df.index:
            print (symbol)
            try:
                url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
                driver.get(url)
                time.sleep(.5)
                
                html = driver.page_source
                soup = bs(html, features="lxml")
                for m in df.columns:
                    df.loc[symbol, m] = fundamental_metric(soup, m)
            except:
                continue
        return df
        
    def fundamental_metric(soup, metric):
        return soup.find(text=metric).find_next(class_='snapshot-td2').text
    
    df = pd.DataFrame(index=stock_list, columns=metric)
    df = get_fundamental_data(df)
    print("All stocks with fundamental data: ")
    print(df)
    
    if stock_list == si.tickers_dow():
        path = f'/Users/shashank/Documents/Code/Python/Outputs/finviz_fundamentals/dow/{today}.csv'
        df.to_csv(path)
    elif stock_list == si.tickers_sp500():
        path = f'/Users/shashank/Documents/Code/Python/Outputs/finviz_fundamentals/sp500/{today}.csv'
        df.to_csv(path)
    else:
        path = f'/Users/shashank/Documents/Code/Python/Outputs/finviz_fundamentals/{today}.csv'
        df.to_csv(path)
        
    driver.close()
    
stock_list = pd.read_csv('/Users/shashank/Documents/Code/Python/Research/nasdaq100/nasdaq100_tickers.csv')['Ticker'].tolist()
metric = ['Dividend',
          'Dividend %',
          'P/E',
          'Forward P/E',
          'PEG',
          'P/B',
          'Debt/Eq',
          'EPS (ttm)',
          'Dividend %',
          'ROE',
          'ROI',
          'EPS Q/Q',
          'EPS (ttm)',
          'Earnings',
          'Insider Own',
          'Quick Ratio',
          'Current Ratio',
          'Short Ratio',
          'Volatility',
          'ATR',
          'Beta'
          ]
finviz_parser(stock_list, metric)

# =============================================================================
# if stock_list == si.tickers_dow():
#     path = f'/Users/shashank/Documents/Code/Python/Outputs/finviz_fundamentals/dow/{today}.csv'
#     df = pd.read_csv(path, index_col=0)
# elif stock_list == si.tickers_sp500():
#     path = f'/Users/shashank/Documents/Code/Python/Outputs/finviz_fundamentals/sp500/{today}.csv'
#     df = pd.read_csv(path, index_col=0)
# else:
#     path = f'/Users/shashank/Documents/Code/Python/Outputs/finviz_fundamentals/{today}.csv'
#     df = pd.read_csv(path, index_col=0)
#  
# print (df)
# =============================================================================