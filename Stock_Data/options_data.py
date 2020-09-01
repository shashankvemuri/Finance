from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import Request, urlopen
pd.set_option('display.max_columns', None)

def get_options_data(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/options?date="
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    html = BeautifulSoup(webpage, "html.parser")
    
    data = pd.read_html(str(html), attrs = {'class': 'calls W(100%) Pos(r) Bd(0) Pt(0) list-options'})[0]
    return data

ticker = input('Enter a ticker: ')
print (get_options_data(ticker))