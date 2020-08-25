import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set up scraper
url = ("https://finviz.com/insidertrading.ashx")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def insider_trades():
    try:
        trades = pd.read_html(str(html), attrs = {'class': 'body-table'})[0]
        trades.columns = ['Ticker', 'Owner', 'Relationship', 'Date', 'Transaction', 'Cost', '#Shares', 'Value', '#Shares Total', 'SEC Form 4']
        trades = trades.sort_values('Date', ascending=False)
        trades = trades.set_index('Date')
        trades = trades.drop('Date')
        trades = trades.iloc[2:]
        return trades.head()
    except Exception as e:
        return e

print ('\nInsider Trades: ')
print(insider_trades())