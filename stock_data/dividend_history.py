# Import dependencies
from datetime import datetime, timedelta
import time
import requests
import pandas as pd
from lxml import html

# Prompt the user to input a ticker symbol
symbol = input("Enter a ticker: ").upper()

# Define the start and end dates
start = datetime.today() - timedelta(days=9125)
end = datetime.today()

def format_date(date_datetime):
    """Converts a datetime object into a string representation of the date."""
    date_timetuple = date_datetime.timetuple()
    date_mktime = time.mktime(date_timetuple)
    date_int = int(date_mktime)
    date_str = str(date_int)
    return date_str

def subdomain(symbol, start, end):
    """Constructs the URL for retrieving dividend history from Yahoo Finance."""
    format_url = "{0}/history?period1={1}&period2={2}"
    tail_url = "&interval=div%7Csplit&filter=div&frequency=1d"
    subdomain = format_url.format(symbol, start, end) + tail_url
    return subdomain

def header(subdomain):
    """Defines the HTTP headers to be used in the request to retrieve the dividend history."""
    hdrs = {
        "authority": "finance.yahoo.com",
        "method": "GET",
        "path": subdomain,
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": "cookies",
        "dnt": "1",
        "pragma": "no-cache",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0"
    }
    return hdrs

def scrape_page(url, header):
    """Retrieves the dividend history table from the specified URL and returns a Pandas DataFrame."""
    page = requests.get(url, headers=header)
    element_html = html.fromstring(page.content)
    table = element_html.xpath('//table')
    table_tree = html.tostring(table[0], method='xml')
    df = pd.read_html(table_tree)
    return df

def clean_dividends(symbol, dividends):
    """Cleans the retrieved dividend data and outputs a Pandas Series object."""
    index = len(dividends)
    dividends = dividends.drop(index-1)
    dividends = dividends.set_index('Date')
    dividends = dividends['Dividends']
    dividends = dividends.str.replace(r'\Dividend', '')
    dividends = dividends.astype(float)
    dividends.name = symbol
    return dividends

if __name__ == '__main__':
    # Convert the start and end dates into string format
    start = format_date(start)
    end = format_date(end)

    # Construct the URL for retrieving the dividend history
    sub = subdomain(symbol, start, end)

    # Define the HTTP headers for the request
    hdrs = header(sub)

    # Retrieve the dividend history table and clean the data
    base_url = "https://finance.yahoo.com/quote/"
    url = base_url + sub
    dividends_df = scrape_page(url, hdrs)
    dividends = clean_dividends(symbol, dividends_df[0])

    # Print the cleaned dividend data
    print(dividends)