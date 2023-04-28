# Import required libraries
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

# Set display options for pandas
pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Define URL and request headers
url = "https://finviz.com/"
headers = {'User-Agent': 'Mozilla/5.0'}

# Send request to the website and parse the HTML
req = Request(url, headers=headers)
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

# Define functions to scrape data from different sections of the page
def get_top_stocks():
    try:
        # Scrape the top up stocks section of the page
        ups = pd.read_html(str(html), attrs={'class': 't-home-table'})[0]
        ups.columns = ['Ticker', 'Last', 'Change', 'Volume', '4', 'Signal']
        ups = ups.drop(columns=['4'])
        ups = ups.iloc[1:]
        ups = ups.set_index('Ticker')
        return ups
    except Exception as e:
        # Return the exception if there is an error
        return e

def get_bottom_stocks():
    try:
        # Scrape the top down stocks section of the page
        downs = pd.read_html(str(html), attrs={'class': 't-home-table'})[1]
        downs.columns = ['Ticker', 'Last', 'Change', 'Volume', '4', 'Signal']
        downs = downs.drop(columns=['4'])
        downs = downs.iloc[1:]
        downs = downs.set_index('Ticker')
        return downs
    except Exception as e:
        # Return the exception if there is an error
        return e

def get_signals():
    try:
        # Scrape the top signals section of the page
        sig1 = pd.read_html(str(html), attrs={'class': 't-home-table'})[2]
        sig1.columns = ['Ticker', 'Ticker', 'Ticker', 'Ticker', '4', 'Signal']
        sig1 = sig1.drop(columns=['4'])
        sig1 = sig1[1:]
        
        sig2 = pd.read_html(str(html), attrs={'class': 't-home-table'})[3]
        sig2.columns = ['Ticker', 'Ticker', 'Ticker', 'Ticker', '4', 'Signal']
        sig2 = sig2.drop(columns=['4'])
        sig2 = sig2[1:]
        
        frames = [sig1, sig2]
        signals = pd.concat(frames)
        signals = signals.set_index('Ticker')
        return signals
    except Exception as e:
        # Return the exception if there is an error
        return e

def get_headlines():
    try:
        # Scrape the headlines section of the page
        headlines = pd.read_html(str(html), attrs={'class': 't-home-table'})[4]
        headlines.columns = ['0', 'Time', 'Headlines']
        headlines = headlines.drop(columns=['0'])
        headlines = headlines[1:]
        headlines = headlines.set_index('Time')
        return headlines
    except Exception as e:
        # Return the exception if there is an error
        return e

def get_major_news():
    try:
        # Scrape the major news section of the page
        major = pd.read_html(str(html), attrs={'class': 't-home-table'})[6]
        major.columns = ['Ticker', 'Change']
        major = major[1:]
        major = major.set_index('Ticker')
        return major
    except Exception as e:
        return e

def get_earnings():
    try:
        # Scrape the earnings section of the page
        earnings = pd.read_html(str(html), attrs = {'class': 't-home-table'})[7]
        earnings.columns = ['Date', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker']
        earnings = earnings.iloc[1:]
        earnings = earnings.set_index('Ticker')
        return earnings
    except Exception as e:
        return e

def get_futures():
    try:
        # Scrape the futures section of the page
        futures1 = pd.read_html(str(html), attrs = {'class': 't-home-table'})[8]
        futures1.columns = ['Index', 'Last', 'Change', 'Change (%)', '4']
        futures1 = futures1.drop(columns = ['4'])
        futures1 = futures1.iloc[1:]
        
        futures2 = pd.read_html(str(html), attrs = {'class': 't-home-table'})[9]
        futures2.columns = ['Index', 'Last', 'Change', 'Change (%)', '4']
        futures2 = futures2.drop(columns = ['4'])
        futures2 = futures2.iloc[1:]
        
        frames = [futures1, futures2]
        futures = pd.concat(frames)
        futures = futures.set_index('Index')
        futures = futures.dropna()
        return futures
    except Exception as e:
        return e
    
# Print out the resulting dataframes for each category
print ('\nTop Up Stocks: ')
print(get_top_stocks())

print ('\nBottom Stocks: ')
print(get_bottom_stocks())

print ('\nTop Signals: ')
print(get_signals())

print ('\nHeadlines: ')
print(get_headlines())

print ('\nMajor News: ')
print(get_major_news())

print ('\nUpcoming Earnings: ')
print(get_earnings())

print ('\nFutures: ')
print(get_futures())