import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import pandas as pd
from pandasgui import show

pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set up scraper
url = ("https://finviz.com/news.ashx")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

def news():
    try:
        news = pd.read_html(str(html))[5]
        news.columns = ['0', 'Time', 'Headlines']
        news = news.drop(columns = ['0'])
        news = news.set_index('Time')
        return news
    except Exception as e:
        return e

print ('\nNews: ')
print(news())

def blog_news():
    try:
        news = pd.read_html(str(html))[6]
        news.columns = ['0', 'Time', 'Headlines']
        news = news.drop(columns = ['0'])
        news = news.set_index('Time')
        return news
    except Exception as e:
        return e

print ('\nNews: ')
print(news())

gui = show(news())

# print ('\nBlog News: ')
# print(blog_news())