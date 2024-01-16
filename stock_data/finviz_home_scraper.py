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
html_content = soup(webpage, "html.parser")

# Function to scrape a section of the page
def scrape_section(html, attrs, columns, drop_columns, index_column, idx=0):
    try:
        data = pd.read_html(str(html), attrs=attrs)[idx]
        data.columns = columns
        data.drop(columns=drop_columns, inplace=True)
        data.set_index(index_column, inplace=True)
        return data
    except Exception as e:
        return pd.DataFrame({'Error': [str(e)]})

# Scrape different sections of the page and print the results
print('\nPositive Stocks: ')
print(scrape_section(html_content, {'class': 'styled-table-new is-rounded is-condensed is-tabular-nums'}, 
                     ['Ticker', 'Last', 'Change', 'Volume', '4', 'Signal'], ['4'], 'Ticker'))

print('\nNegative Stocks: ')
print(scrape_section(html_content, {'class': 'styled-table-new is-rounded is-condensed is-tabular-nums'}, 
                     ['Ticker', 'Last', 'Change', 'Volume', '4', 'Signal'], ['4'], 'Ticker', idx=1))

print('\nHeadlines: ')
print(scrape_section(html_content, {'class': 'styled-table-new is-rounded is-condensed hp_news-table table-fixed'}, 
                     ['0', 'Time', 'Headlines'], ['0'], 'Time'))

print('\nUpcoming Releases: ')
print(scrape_section(html_content, {'class': 'calendar_table'}, 
                     ['Date', 'Time', '2', 'Release', 'Impact', 'For', 'Actual', 'Expected', 'Prior'], ['2'], 'Date'))

print('\nUpcoming Earnings: ')
print(scrape_section(html_content, {'class': 'styled-table-new is-rounded is-condensed hp_table-earnings'}, 
                     ['Date', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker', 'Ticker'], [], 'Ticker'))

print('\nFutures: ')
print(scrape_section(html_content, {'class': 'styled-table-new is-rounded is-condensed is-tabular-nums'}, 
                     ['Index', 'Last', 'Change', 'Change (%)'], [], 'Index', idx=2))

print('\Forex/Rates: ')
print(scrape_section(html_content, {'class': 'styled-table-new is-rounded is-condensed is-tabular-nums'}, 
                     ['Index', 'Last', 'Change', 'Change (%)'], [], 'Index', idx=3))