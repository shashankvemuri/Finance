import pandas as pd
from selenium import webdriver
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options
from yahoo_fin import stock_info as si
import datetime 
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome('../chromedriver', options=options)

symbol = input('Enter a ticker: ')
print ('Getting data for ' + symbol)

try:
    url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
    driver.get(url)
    time.sleep(.5)
    
    html = driver.page_source
    soup = bs(html, features="lxml")
    fundamentals = pd.read_html(html, attrs = {'class': 'snapshot-table2'})[0]
    news = pd.read_html(html, attrs = {'class': 'fullview-news-outer'})[0]
    insider = pd.read_html(html, attrs = {'class': 'body-table'})[0]
    
    # Clean up fundamentals dataframe
    fundamentals.columns = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    colOne = []
    colLength = len(fundamentals)
    for k in np.arange(0, colLength, 2):
        colOne.append(fundamentals[f'{k}'])
    attrs = pd.concat(colOne, ignore_index=True)

    colTwo = []
    colLength = len(fundamentals)
    for k in np.arange(1, colLength, 2):
        colTwo.append(fundamentals[f'{k}'])
    vals = pd.concat(colTwo, ignore_index=True)
    
    fundamentals = pd.DataFrame()
    fundamentals['Attributes'] = attrs
    fundamentals['Values'] = vals
    fundamentals = fundamentals.set_index('Attributes')
    print ('-'*75)
    print (f'Fundamental Ratios for {symbol}')
    print (fundamentals)

    # Clean up news dataframe
    news.columns = ['Date', 'News']
    news = news.set_index('Date')
    print ('-'*75)
    print (f'News for {symbol}')
    print (news)
    
    # Clean up insider dataframe
    insider = insider.iloc[1:]
    insider.columns = ['Trader', 'Relationship', 'Date', 'Transaction', 'Cost', '# Shares', 'Value ($)', '#Shares Total', 'SEC Form 4']
    insider = insider.set_index('Date')
    print ('-'*75)
    print (f'Insider Trading for {symbol}')
    print (insider)
    
    driver.close()
except Exception as e:
    print (f'Could not get the data for {symbol} because {e}')
    driver.close()